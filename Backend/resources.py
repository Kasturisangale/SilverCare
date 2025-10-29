import builtins
from collections import OrderedDict
import csv
from datetime import date, timedelta, datetime
from zoneinfo import ZoneInfo
import pytz
from functools import wraps
import io
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import pandas as pd
from flask import request, jsonify
from flask_restx import Resource, Namespace, reqparse, marshal, fields
from flask_jwt_extended import create_access_token, current_user, get_jwt_identity, jwt_required, get_jwt, verify_jwt_in_request, JWTManager
from sqlalchemy import distinct, exists, func, null,extract
from sqlalchemy.orm import aliased, joinedload, subqueryload, contains_eager
import logging
import traceback


from Backend.models import *
# from .api_models import *
# from .helper import *

from werkzeug.datastructures import FileStorage
from werkzeug.exceptions import Unauthorized

logger = logging.getLogger(__name__)

authorizations = {
    "jsonwebtoken": {
        "type": "apiKey",
        "in": "header",
        "name": "Authorization"
    }
}

sc = Namespace("sc", description="SilverCare Backend API Namespace", authorizations=authorizations)

user_update_model = sc.model('UserUpdate', {
    'first_name': fields.String(required=False),
    'last_name': fields.String(required=False),
    'username': fields.String(required=False),
    'role': fields.String(required=False),
    'profile_picture': fields.String(required=False),
})

create_medicine_model = sc.model('CreateMedicine', {
    'title': fields.String(required=True),
    'description': fields.String(required=True),
    'image': fields.String(required=False),
})

assign_medicine_model = sc.model('AssignMedicine', {
    'medicine_id': fields.Integer(required=True),
    'senior_citizen_id': fields.Integer(required=False),
    'dosage': fields.String(required=True),
    'start_date': fields.String(required=True, description='YYYY-MM-DD'),
    'end_date': fields.String(description='YYYY-MM-DD'),
    'breakfast_before': fields.Boolean(required=False, default=False),
    'breakfast_after': fields.Boolean(required=False, default=False),
    'lunch_before': fields.Boolean(required=False, default=False),
    'lunch_after': fields.Boolean(required=False, default=False),
    'dinner_before': fields.Boolean(required=False, default=False),
    'dinner_after': fields.Boolean(required=False, default=False),
})

unassign_medicine_model = sc.model('UnassignMedicine', {
    'user_id': fields.Integer(required=False, description='Senior Citizen ID'),
    'medicine_id': fields.Integer(required=True, description='ID of medicine to be removed'),
})

report_model = sc.model("StatusReportInput", {
    "user_id": fields.Integer(required=False, description="Senior Citizen ID"),

    "month": fields.Integer(required=True, description="Month (1-12)"),
    "year": fields.Integer(required=True, description="Year (e.g., 2025)")
})

medicine_reminder_model = sc.model("MedicineReminder", {
    "reminder_id": fields.Integer(required=True),
    "user_med_map_id": fields.Integer(required=True),
    "reminder_time": fields.String(required=True, example="breakfast_before"),
    "notification_type": fields.String(required=True, example="push"),
    "message": fields.String(required=True),
    "active": fields.Boolean(default=True),
})

list_medicine_reminder_model = sc.model("ListMedicineReminder", {
    "user_med_map_id": fields.Integer(required=True)
})

send_reminder_model = sc.model('SendReminderModel', {
    'user_id': fields.Integer(required=True, description='ID of the user to send reminder to'),
    'medicine_id': fields.Integer(required=True, description='ID of the medicine to send reminder for')
})

mark_medicine_taken_model = sc.model("MarkMedicineTaken", {
    'medicine_id': fields.Integer(required=True),
    'slot': fields.String(required=True, example="breakfast_before"),
})

health_entry_model = sc.model("HealthEntry", {
    'bp_systolic': fields.Integer(required=True),
    'bp_diastolic': fields.Integer(required=True),
    'sugar_level': fields.Float(required=True),
})

# To verify token
@sc.route("/api/verify-token")
class VerifyToken(Resource):
    
    def get(self):
        "Verify JWT token"
        try:
            # Verify the JWT in the request
            verify_jwt_in_request()  # Raises an exception if the token is invalid
            claims = get_jwt()  # Extract claims from the token
            return {
                "valid": True,
                "claims": claims,
                "message": "Token is valid",
                "role": claims.get('role')

            }, 200
        except Unauthorized as e:
            return {
                "valid": False,
                "message": "Invalid or expired token"
            }, 401
        except Exception as e:
            return {
                "valid": False,
                "message": "An error occurred during token verification"
            }, 500
        
# Edit user
@sc.route('/user/<int:user_id>')
class EditUser(Resource):
    @jwt_required()
    @sc.expect(user_update_model, validate=True)
    def put(self, user_id):
        """Update user details"""
        data = request.get_json()
        user_id = current_user.id # Only concerned user can only change it's own details
        user = User.query.get(user_id)

        if not user:
            return {'message': 'User not found'}, 404        
        # to check validity of user
        if (user_id != user):
            return {'message': 'You are not authorized to update other user details'}, 403

        # Update fields only if present in data
        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name)
        user.username = data.get('username', user.username)
        user.role = data.get('role', user.role)
        user.profile_picture = data.get('profile_picture', user.profile_picture)

        # Handling password update (only if provided and not empty)
        if 'password' in data and data['password']:
            user.set_password(data['password'])

        try:
            db.session.commit()
            return {'message': 'User updated successfully'}, 200
        except Exception as e:
            db.session.rollback()
            return {'message': 'Failed to update user', 'error': str(e)}, 500

# <------------------------------------CRUD operations for Medicine------------------------------------>


#Create medicine
@sc.route('/create-medicine', methods=["POST", "OPTIONS"])
class CreateMedicine(Resource):
    @jwt_required()
    @sc.expect(create_medicine_model, validate=True)
    def post(self):
        """Create new medicine entry"""
        data = request.get_json()
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        medicine = Medicine(
            title=data['title'],
            description=data['description'],
            user_id=user_id,
            image=data.get('image')
        )

        if (user.role == "admin"):
            medicine.status = "approved"
        else:
            medicine.status = "pending"

        try:
            db.session.add(medicine)
            db.session.commit()
            return {'message': 'Medicine created successfully', 'medicine_id': medicine.id}, 201
        except Exception as e:
            db.session.rollback()
            return {'message': 'Failed to create medicine', 'error': str(e)}, 500
        
    def options(self):
        return {}, 200 
        
#Get all medicines
@sc.route('/all-medicines', methods=["GET", "OPTIONS"])
class AllMedicineNames(Resource):
    def get(self):
        """Get all medicine names"""
        medicines = Medicine.query.filter_by(status="approved").all()

        result = [
            {
                "id": med.id,
                "title": med.title,
                "description": med.description,
                "image": med.image
            }
            for med in medicines
        ]
        return {"medicines": result}, 200
    def options(self):
        return {}, 200

@sc.route('/edit-medicine/<int:medicine_id>', methods=["PUT", "OPTIONS"])
class EditMedicine(Resource):
    @jwt_required()
    @sc.expect(create_medicine_model, validate=True)
    def put(self, medicine_id):
        """Update a medicine entry by ID."""
        user_id = get_jwt_identity()
        user_role = current_user.role

        if user_role != "admin":
            return {'message': 'Unauthorized'}, 403
        # Check if the medicine exists and belongs to the user
        medicine = Medicine.query.filter_by(id=medicine_id).first()

        if not medicine:
            return {'message': 'Medicine not found or unauthorized'}, 404

        data = request.get_json()
        medicine.title = data.get('title', medicine.title)
        medicine.description = data.get('description', medicine.description)
        medicine.image = data.get('image', medicine.image)

        try:
            db.session.commit()
            return {'message': 'Medicine updated successfully'}, 200
        except Exception as e:
            db.session.rollback()
            return {'message': 'Failed to update medicine', 'error': str(e)}, 500

    def options(self,medicine_id):
        """Handle OPTIONS request for CORS pre-flight."""
        return {}, 200  # Respond with 200 status for pre-flight requests

# Delete medicine
@sc.route('/delete-medicine/<int:medicine_id>', methods=["DELETE", "OPTIONS"])
class DeleteMedicine(Resource):
    @jwt_required()
    def delete(self, medicine_id):
        """Delete a medicine entry by ID."""
        user_id = get_jwt_identity()
        user_role = current_user.role

        if user_role != "admin":
            return {'message': 'Unauthorized'}, 403
        
        medicine = Medicine.query.filter_by(id=medicine_id).first()

        if not medicine:
            return {'message': 'Medicine not found or unauthorized'}, 404

        try:
            db.session.delete(medicine)
            db.session.commit()
            return {'message': 'Medicine deleted successfully'}, 200
        except Exception as e:
            db.session.rollback()
            return {'message': 'Failed to delete medicine', 'error': str(e)}, 500

    def options(self,medicine_id):
        """Handle OPTIONS request"""
        return {}, 200  # Return a 200 response with no content, as it's a pre-flight request

#<---------------------------------------------------------------------------------------------------------------->


# <------------------------------------CRUD operations to assign-medicine------------------------------------>

# To assign medicine to senior citizen
@sc.route("/assign-medicine", methods=["POST"])
class AssignMedicine(Resource):
    @jwt_required()
    @sc.expect(assign_medicine_model, validate=True)
    def post(self):
        """Assign a medicine to a senior citizen."""
        data = request.get_json()
        user_role = current_user.role

        if(user_role == "senior_citizen"):
            user_id = current_user.id
        elif user_role == "care_giver":
            user_id = data.get("senior_citizen_id")
            if not user_id:
                return {"error": "Missing 'senior_citizen_id' for caregiver"}, 400

            # Check caregiver-senior relationship
            is_approved = CaregiverSeniorMap.query.filter_by(
                caregiver_id=current_user.id,
                senior_id=user_id,
                status='approved'
            ).first()

            if not is_approved:
                return {"error": "You are not an approved caregiver for this senior citizen."}, 403
        
        try:
            existing_assignment = UserMedMap.query.filter(
            UserMedMap.user_id == user_id,
            UserMedMap.medicine_id == data["medicine_id"]
            ).first()
            if existing_assignment:
                return {
                    "message": "This medicine is already assigned."
                }, 400
            start_date_obj = datetime.strptime(data["start_date"], "%Y-%m-%d")
            if not data.get("end_date"):
                end_date_obj = start_date_obj + timedelta(days=30)
            else:
                end_date_obj = datetime.strptime(data["end_date"], "%Y-%m-%d")

            assignment = UserMedMap(
                user_id=user_id,
                medicine_id=data["medicine_id"],
                dosage=data["dosage"],
                start_date=start_date_obj,
                end_date=end_date_obj,
                breakfast_before=data.get("breakfast_before", False),
                breakfast_after=data.get("breakfast_after", False),
                lunch_before=data.get("lunch_before", False),
                lunch_after=data.get("lunch_after", False),
                dinner_before=data.get("dinner_before", False),
                dinner_after=data.get("dinner_after", False),
            )
            m=Medicine.query.filter_by(id=assignment.medicine_id).first()
            title=m.title
            db.session.add(assignment)
            db.session.commit()
            return {"message": "Medicine assigned and status tracking initialized.",
                    "medication": {
                    "id": assignment.id,
                    "medicine_id": assignment.medicine_id,
                    "medicineTitle":title,
                    "dosage": assignment.dosage,
                    "start_date": assignment.start_date.isoformat(),
                    "end_date": assignment.end_date.isoformat(),
                    "breakfast_before": assignment.breakfast_before,
                    "breakfast_after": assignment.breakfast_after,
                    "lunch_before": assignment.lunch_before,
                    "lunch_after": assignment.lunch_after,
                    "dinner_before": assignment.dinner_before,
                    "dinner_after": assignment.dinner_after
                }}, 201
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

@sc.route("/medication/<int:map_id>", methods=["PUT"])
class UpdateMedicineMapping(Resource):
    @jwt_required()
    def put(self, map_id):
        """Update medicine mapping in UserMedMap; apply slot changes only from current slot onward"""
        from datetime import datetime
        user = current_user
        data = request.get_json()

        # Slot time ranges (start_hour, end_hour)
        slot_times = {
            "breakfast_before": (4, 10),
            "breakfast_after": (4, 10),
            "lunch_before": (10, 16),
            "lunch_after": (10, 16),
            "dinner_before": (16, 23),
            "dinner_after": (16, 23)
        }

        today = datetime.utcnow().date()
        now_hour = datetime.utcnow().hour

        # --- Get mapping record ---
        med_mapping = UserMedMap.query.get(map_id)
        if not med_mapping:
            return {"error": "Medicine mapping not found."}, 404

        # --- Role Based Checks ---
        if user.role == "care_giver":
            relation = CaregiverSeniorMap.query.filter_by(
                caregiver_id=user.id,
                senior_id=med_mapping.user_id,
                status='approved'
            ).first()
            if not relation:
                return {"error": "You are not authorized to update this medication."}, 403

        elif user.role == "senior_citizen":
            if med_mapping.user_id != user.id:
                return {"error": "You can only update your own medications."}, 403
        else:
            return {"error": "Access denied"}, 403

        try:
            if "dosage" in data:
                if str(data["dosage"]).isdigit():
                    return {"error": "Dosage must include units (e.g., '1 pill', '10mg')."}, 400
                med_mapping.dosage = data["dosage"]

            if "start_date" in data:
                med_mapping.start_date = datetime.strptime(data["start_date"], "%Y-%m-%d").date()

            if "end_date" in data or "endDate" in data:
                incoming_val = data.get("end_date") or data.get("endDate")
                med_mapping.end_date = datetime.strptime(incoming_val, "%Y-%m-%d").date()

            # --- Slot updates ---
            for field in [
                "breakfast_before", "breakfast_after",
                "lunch_before", "lunch_after",
                "dinner_before", "dinner_after"
            ]:
                if field in data:
                    new_val = bool(data[field])
                    old_val = getattr(med_mapping, field)

                    #  Update mapping template (affects future Status creation)
                    setattr(med_mapping, field, new_val)

                    #  Update existing Status rows from today onwards 
                    for status_row in med_mapping.statuses:
                        status_date = status_row.date.date()

                        # Skip past days completely
                        if status_date < today:
                            continue

                        # Skip today's past slots
                        if status_date == today:
                            start_hour, end_hour = slot_times[field]
                            if now_hour >= end_hour:
                                continue  # this slot time has passed today

                        # Removal (True->False) → None
                        if not new_val and old_val:
                            setattr(status_row, field, None)
                        # Addition (False->True) → False (not yet taken)
                        elif new_val and not old_val:
                            setattr(status_row, field, False)

            db.session.commit()

            return {
                "message": "Medication mapping updated successfully",
                "medication": {
                    "id": med_mapping.id,
                    "medicine_id": med_mapping.medicine_id,
                    "medicineTitle": med_mapping.medicine.title if med_mapping.medicine else None,
                    "dosage": med_mapping.dosage,
                    "start_date": med_mapping.start_date.isoformat(),
                    "end_date": med_mapping.end_date.isoformat() if med_mapping.end_date else None,
                    "breakfast_before": med_mapping.breakfast_before,
                    "breakfast_after": med_mapping.breakfast_after,
                    "lunch_before": med_mapping.lunch_before,
                    "lunch_after": med_mapping.lunch_after,
                    "dinner_before": med_mapping.dinner_before,
                    "dinner_after": med_mapping.dinner_after
                }
            }, 200

        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

# To unassign medicine for senior citizen
@sc.route("/unassign-medicine", methods=["DELETE"])
class UnassignMedicine(Resource):
    @jwt_required()
    @sc.expect(unassign_medicine_model, validate=True)
    def delete(self):
        data = request.get_json()
        user_role = current_user.role

        if user_role == "senior_citizen":
            user_id = current_user.id
        elif user_role == "care_giver":
            user_id = data.get("senior_citizen_id")
            if not user_id:
                return {"error": "Missing 'senior_citizen_id' for caregiver"}, 400

            is_approved = CaregiverSeniorMap.query.filter_by(
                caregiver_id=current_user.id,
                senior_id=user_id,
                status='approved'
            ).first()
            if not is_approved:
                return {"error": "You are not an approved caregiver for this senior citizen."}, 403
        else:
            return {"error": "Role not authorized"}, 403

        medicine_id = data['medicine_id']
        assignment = UserMedMap.query.filter_by(
            user_id=user_id, medicine_id=medicine_id
        ).first()
        if not assignment:
            return {"error": "Assignment not found."}, 404

        try:
            db.session.commit()
            return {"message": "Medicine unassigned successfully."}, 200
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

#<------------------------To get all medicines assigned to a senior citizen-------------------------------------->
@sc.route('/my-medicines')
@sc.doc(descriptions='Get all medicines assigned to a senior citizen')
class MyMedicines(Resource):
    @jwt_required()
    def get(self):
        """Get all medicines assigned to a senior citizen."""
        try:
            user_id = get_jwt_identity()

            current_user = User.query.get(user_id)
            if not current_user:
                return {
                    "error": "User not found.",
                    "code": "USER_NOT_FOUND"
                }, 404

            if current_user.role != "senior_citizen":
                return {
                    "error": "You are not authorized to access this resource.",
                    "code": "FORBIDDEN_ROLE"
                }, 403

            user_meds = UserMedMap.query.filter_by(user_id=user_id).all()
            if not user_meds:
                return {
                    "error": "No medicines found for this user.",
                    "code": "NO_MEDICINES"
                }, 404

            def get_assigned_slots(um):
                slots = []
                if um.breakfast_before:
                    slots.append('Before Breakfast')
                if um.breakfast_after:
                    slots.append('After Breakfast')
                if um.lunch_before:
                    slots.append('Before Lunch')
                if um.lunch_after:
                    slots.append('After Lunch')
                if um.dinner_before:
                    slots.append('Before Dinner')
                if um.dinner_after:
                    slots.append('After Dinner')
                return slots

            result = []
            for um in user_meds:
                med = um.medicine

                if not med:
                    continue  # skip if medicine relation broken

                result.append({
                    "medicine_id": med.id,
                    "title": med.title,
                    "description": med.description,
                    "dosage": um.dosage,
                    "start_date": um.start_date.isoformat() if um.start_date else None,
                    "end_date": um.end_date.isoformat() if um.end_date else None,
                    "image": med.image,
                    "is_approved": med.is_approved,
                    "assigned_slots": get_assigned_slots(um)
                })

            return {
                "medicines": result
            }, 200

        except SQLAlchemyError as e:
            return {
                "error": "Database error occurred.",
                "details": str(e),
                "code": "DB_ERROR"
            }, 500

        except Exception as e:
            return {
                "error": "An unexpected error occurred.",
                "details": str(e),
                "code": "INTERNAL_SERVER_ERROR"
            }, 500

# <---------------------------------------------------------------------------------------------------------------->

# <------------------------------------Getting Status of medicine------------------------------------>

# getting medicine status
@sc.route("/medicine-status/<int:medicine_id>", methods=["GET"])
class MedicineStatus(Resource):
    @jwt_required()
    @sc.doc(params={
        'date': 'Date in YYYY-MM-DD format (as query parameter)'
    })
    def get(self, medicine_id):
        """Get the status of a specific medicine for a senior citizen."""
        try:
            user_id = get_jwt_identity()
            date_str = request.args.get('date')
            
            if not date_str:
                return {
                    "error": "Date is required in 'YYYY-MM-DD' format as a query parameter.",
                    "code": "DATE_MISSING"
                }, 400
            
            try:
                target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                return {
                    "error": "Invalid date format. Use 'YYYY-MM-DD'.",
                    "code": "INVALID_DATE_FORMAT"
                }, 400

            # Find assigned medicine for user
            user_med_map = UserMedMap.query.filter_by(user_id=user_id, medicine_id=medicine_id).first()
            if not user_med_map:
                return {
                    "error": "Medicine assignment not found.",
                    "code": "MEDICINE_ASSIGNMENT_NOT_FOUND"
                }, 404

            # Find status entry by date
            status = Status.query.filter_by(user_med_map_id=user_med_map.id, date=target_date).first()
            if not status:
                return {
                    "error": "No status entry found for this date.",
                    "code": "STATUS_NOT_FOUND"
                }, 404

            return {
                "medicine_id": medicine_id,
                "date": target_date.isoformat(),
                "statuses": {
                    "breakfast_before": status.breakfast_before,
                    "breakfast_after": status.breakfast_after,
                    "lunch_before": status.lunch_before,
                    "lunch_after": status.lunch_after,
                    "dinner_before": status.dinner_before,
                    "dinner_after": status.dinner_after
                }
            }, 200
        
        # Database or ORM-related failures
        except SQLAlchemyError as e:
            return {
                "error": "Database error occurred while fetching medicine status.",
                "code": "DB_ERROR",
                "details": str(e)
            }, 500

        # Unexpected errors
        except Exception as e:
            return {
                "error": "An unexpected error occurred.",
                "code": "INTERNAL_SERVER_ERROR",
                "details": str(e)
            }, 500
        
# TO get report of medicine status
@sc.route("/status-report", methods=["POST"])
@sc.doc(description="Generates a monthly medicine status report for a senior citizen or by a caregiver for their mapped senior.")
class StatusReport(Resource):
    @jwt_required()
    @sc.expect(report_model, validate=True)
    def post(self):
        """Generates a monthly medicine status report for a senior citizen or by a caregiver for their mapped senior."""
        # user_id = get_jwt_identity()
        user_role = current_user.role
        data = request.get_json()
        month = data.get("month")
        year = data.get("year")

        if(user_role == "senior_citizen"):
            user_id = current_user.id
        elif user_role == "care_giver":
            user_id = data.get("user_id")
            if not user_id:
                return {"error": "Missing 'senior citizen id' for caregiver"}, 400
            # Check caregiver-senior relationship
            is_approved = CaregiverSeniorMap.query.filter_by(
                caregiver_id=current_user.id,
                senior_id=user_id,
                status='approved'
                ).first()
            
            if not is_approved:
                return {"error": "You are not an approved caregiver for this senior citizen."}, 403
            
        if month is None or year is None:
            return {"error": "Month and year are required in JSON body."}, 400

        med_maps = UserMedMap.query.filter_by(user_id=user_id).all()
        statuses = []
        for map in med_maps:
            for s in map.statuses:
                if s.date.month == month and s.date.year == year:
                    statuses.append(s)

        result = {}
        for status in statuses:
            date_str = status.date.strftime('%Y-%m-%d')
            slot_statuses = {
                "breakfast_before": status.breakfast_before,
                "breakfast_after": status.breakfast_after,
                "lunch_before": status.lunch_before,
                "lunch_after": status.lunch_after,
                "dinner_before": status.dinner_before,
                "dinner_after": status.dinner_after
            }
            taken = sum(1 for v in slot_statuses.values() if v is True)
            missed = sum(1 for v in slot_statuses.values() if v is False)
            if date_str in result:
                result[date_str]["taken"] += taken
                result[date_str]["missed"] += missed
            else:
                result[date_str] = {
                    "taken": taken,
                    "missed": missed
                }

        return result, 200

        # Handle DB errors
        # except SQLAlchemyError as e:
        #     return {
        #         "error": "Database error occurred while fetching status report.",
        #         "code": "DB_ERROR",
        #         "details": str(e)
        #     }, 500

        # # Handle all unexpected exceptions
        # except Exception as e:
        #     return {
        #         "error": "An unexpected error occurred.",
        #         "code": "INTERNAL_SERVER_ERROR",
        #         "details": str(e)
        #     }, 500


# <------------------------------------Medicine Status for today------------------------------------>

@sc.route('/medicine-status-today')
class MedicineStatusToday(Resource):
    @jwt_required()
    @sc.expect(sc.model('SeniorInput', {
        'senior_citizen_id': fields.Integer(required=True, description='ID of the senior citizen')
    }), validate=True)
    def get(self):
        """Get the status of all medicines for a senior citizen for today."""
        try:
            user_role = current_user.role

            if user_role == "senior_citizen":
                user_id = current_user.id

            elif user_role == "care_giver":
                data = request.get_json()
                user_id = data.get("senior_citizen_id")

                if not user_id:
                    return {
                        "error": "Missing 'senior_citizen_id' for caregiver.",
                        "code": "MISSING_SENIOR_ID"
                    }, 400

                # Check caregiver-senior relationship
                is_approved = CaregiverSeniorMap.query.filter_by(
                    caregiver_id=current_user.id,
                    senior_id=user_id,
                    status='approved'
                ).first()
                if not is_approved:
                    return {
                        "error": "You are not an approved caregiver for this senior citizen.",
                        "code": "CAREGIVER_NOT_APPROVED"
                    }, 403

            else:
                return {
                    "error": "Unauthorized role.",
                    "code": "UNAUTHORIZED_ROLE"
                }, 403

            # Get medicine status for today
            ist = pytz.timezone('Asia/Kolkata')
            current_date = datetime.now(ist).date()

            user_meds = UserMedMap.query.filter_by(user_id=user_id).all()
            completed_meds = []
            pending_meds = []

            for um in user_meds:
                status = Status.query.filter(
                    Status.user_med_map_id == um.id,
                    func.date(Status.date) == current_date
                ).first()

                if not status:
                    continue

                slots = [
                    status.breakfast_before, status.breakfast_after,
                    status.lunch_before, status.lunch_after,
                    status.dinner_before, status.dinner_after
                ]

                valid_slots = [s for s in slots if s is not None]
                if not valid_slots:
                    continue

                med_info = {
                    'medicine_id': um.medicine_id,
                    'medicine_title': um.medicine.title,
                    'dosage': um.dosage
                }

                if all(valid_slots):
                    completed_meds.append(med_info)
                else:
                    pending_meds.append(med_info)

            return {
                'date': current_date.isoformat(),
                'completed_medicines': completed_meds,
                'pending_medicines': pending_meds
            }, 200

        except SQLAlchemyError as e:
            return {
                "error": "A database error occurred while retrieving today's medicine status.",
                "code": "DB_ERROR",
                "details": str(e)
            }, 500

        except Exception as e:
            return {
                "error": "An unexpected error occurred.",
                "code": "INTERNAL_SERVER_ERROR",
                "details": str(e)
            }, 500

#<------------------------------------------------------------------------------------------------------------------>

#<------------------------------------CRUD Operations for Medicine Reminder------------------------------------>
@sc.route('/add-medicine-reminder')
class AddMedicineReminder(Resource):
    @jwt_required()
    @sc.expect(medicine_reminder_model, validate=True)
    def post(self):
        """Add a new medicine reminder"""
        try:
            data = request.get_json()

            # Validate required fields (additional safeguard beyond `validate=True`)
            required_fields = ['user_med_map_id', 'reminder_time', 'notification_type', 'message']
            for field in required_fields:
                if field not in data:
                    return {
                        "error": f"'{field}' is a required field.",
                        "code": "MISSING_FIELD"
                    }, 400

            # Optional: check if user has permission (e.g., only caregivers or seniors can add reminders)
            # Example stub:
            # if current_user.role not in ['senior_citizen', 'care_giver']:
            #     return {"error": "You are not authorized to add reminders.", "code": "FORBIDDEN_ROLE"}, 403

            reminder = MedicineReminder(
                user_med_map_id=data['user_med_map_id'],
                reminder_time=data['reminder_time'],
                notification_type=data['notification_type'],
                message=data['message'],
                active=data.get('active', True)
            )

            db.session.add(reminder)
            db.session.commit()

            return {
                "message": "Reminder created successfully.",
                "id": reminder.id
            }, 201

        except SQLAlchemyError as e:
            db.session.rollback()
            return {
                "error": "A database error occurred while saving the reminder.",
                "code": "DB_ERROR",
                "details": str(e)
            }, 500

        except Exception as e:
            return {
                "error": "An unexpected error occurred.",
                "code": "INTERNAL_SERVER_ERROR",
                "details": str(e)
            }, 500
        
@sc.route('/specific-medicine-reminder')
class ViewMedicineReminder(Resource):
    @jwt_required()
    @sc.doc(params={
        'reminder_id': 'ID of the reminder to fetch'
    })
    def get(self):
        """View a specific medicine reminder by ID (query parameter)"""
        try:
            reminder_id = request.args.get('reminder_id', type=int)

            # Validate query parameter
            if not reminder_id:
                return {
                    "error": "Query parameter 'reminder_id' is required and must be an integer.",
                    "code": "MISSING_REMINDER_ID"
                }, 400

            reminder = MedicineReminder.query.get(reminder_id)

            # Check if reminder exists
            if not reminder:
                return {
                    "error": "Reminder not found for the given ID.",
                    "code": "REMINDER_NOT_FOUND"
                }, 404

            return {
                "id": reminder.id,
                "user_med_map_id": reminder.user_med_map_id,
                "reminder_time": str(reminder.reminder_time),
                "notification_type": reminder.notification_type,
                "message": reminder.message,
                "active": reminder.active
            }, 200

        except SQLAlchemyError as e:
            return {
                "error": "Database error occurred while retrieving the reminder.",
                "code": "DB_ERROR",
                "details": str(e)
            }, 500

        except Exception as e:
            return {
                "error": "An unexpected error occurred.",
                "code": "INTERNAL_SERVER_ERROR",
                "details": str(e)
            }, 500
        
@sc.route('/update-medicine-reminder')
class UpdateMedicineReminder(Resource):
    @jwt_required()
    @sc.expect(medicine_reminder_model, validate=True)
    def put(self):
        """Update a reminder using body data"""
        try:
            data = request.get_json()
            reminder_id = data.get('reminder_id')

            if not reminder_id:
                return {
                    "error": "Field 'reminder_id' is required in the request body.",
                    "code": "MISSING_REMINDER_ID"
                }, 400

            reminder = MedicineReminder.query.get(reminder_id)
            if not reminder:
                return {
                    "error": f"Reminder with ID {reminder_id} not found.",
                    "code": "REMINDER_NOT_FOUND"
                }, 404

            required_fields = ['user_med_map_id', 'reminder_time', 'notification_type', 'message']
            for field in required_fields:
                if field not in data:
                    return {
                        "error": f"'{field}' is a required field.",
                        "code": "MISSING_FIELD"
                    }, 400

            # Update reminder fields
            reminder.user_med_map_id = data['user_med_map_id']
            reminder.reminder_time = data['reminder_time']
            reminder.notification_type = data['notification_type']
            reminder.message = data['message']
            reminder.active = data.get('active', True)

            db.session.commit()

            return {
                "message": "Reminder updated successfully.",
                "id": reminder.id
            }, 200

        except SQLAlchemyError as e:
            db.session.rollback()  # Ensure DB state is clean on failure
            return {
                "error": "Database error occurred while updating the reminder.",
                "code": "DB_ERROR",
                "details": str(e)
            }, 500

        except Exception as e:
            return {
                "error": "An unexpected error occurred.",
                "code": "INTERNAL_SERVER_ERROR",
                "details": str(e)
            }, 500

@sc.route('/list-medicine-reminder')
class ListReminders(Resource):
    @jwt_required()
    @sc.doc(
        params={
            'user_med_map_id': 'ID of the User-Medicine mapping to fetch reminders for'
        },
        description='List all reminders for a specific user_med_map_id'
    )
    def get(self):
        """List all reminders for a specific user_med_map_id"""
        try:
            user_med_map_id = request.args.get('user_med_map_id', type=int)

            if not user_med_map_id:
                return {
                    "error": "Query parameter 'user_med_map_id' is required and must be an integer.",
                    "code": "MISSING_USER_MED_MAP_ID"
                }, 400

            reminders = MedicineReminder.query.filter_by(user_med_map_id=user_med_map_id).all()

            if not reminders:
                return {
                    "error": f"No reminders found for user_med_map_id {user_med_map_id}.",
                    "code": "REMINDERS_NOT_FOUND"
                }, 404

            return [{
                "id": r.id,
                "reminder_time": str(r.reminder_time),
                "notification_type": r.notification_type,
                "message": r.message,
                "active": r.active
            } for r in reminders], 200

        except SQLAlchemyError as e:
            return {
                "error": "Database error occurred while fetching reminders.",
                "code": "DB_ERROR",
                "details": str(e)
            }, 500

        except Exception as e:
            return {
                "error": "An unexpected error occurred.",
                "code": "INTERNAL_SERVER_ERROR",
                "details": str(e)
            }, 500

#<------------------------------------------------------------------------------------------------------------------->


# <------------------------------------Medicine Status for today------------------------------------>

@sc.route('/send-reminder')
class SendMedicineReminder(Resource):
    @jwt_required()
    @sc.expect(send_reminder_model, validate=True)
    def post(self):
        """Send active reminders for a specific medicine"""
        try:
            data = request.get_json()
            user_id = data.get('user_id')
            medicine_id = data.get('medicine_id')

            # Validate required inputs
            if not user_id or not medicine_id:
                return {
                    "error": "Both 'user_id' and 'medicine_id' are required in the request body.",
                    "code": "MISSING_REQUIRED_FIELDS"
                }, 400

            # Check if user-med mapping exists
            user_med_map = UserMedMap.query.filter_by(user_id=user_id, medicine_id=medicine_id).first()
            if not user_med_map:
                return {
                    "error": "Medicine mapping for the user not found.",
                    "code": "USER_MED_MAPPING_NOT_FOUND"
                }, 404

            # Fetch active reminders
            reminders = MedicineReminder.query.filter_by(user_med_map_id=user_med_map.id, active=True).all()
            if not reminders:
                return {
                    "message": "No active reminders found for this medicine.",
                    "medicine_id": medicine_id,
                    "user_id": user_id,
                    "reminders": [],
                    "code": "NO_ACTIVE_REMINDERS"
                }, 200

            # Compose and log/send reminders
            medicine_title = user_med_map.medicine.title if user_med_map.medicine else "Unknown Medicine"
            sent_reminders = []
            for reminder in reminders:
                message = reminder.message or f"Reminder to take {medicine_title} at {reminder.reminder_time}"
                # Simulated notification send (e.g. via email/SMS/push)
                print(f"[{reminder.notification_type.upper()}] To user {user_id}: {message}")

                sent_reminders.append({
                    "type": reminder.notification_type,
                    "time_slot": str(reminder.reminder_time),
                    "message": message
                })

            return {
                "status": "Reminders sent",
                "medicine_id": medicine_id,
                "user_id": user_id,
                "reminders": sent_reminders
            }, 200

        except SQLAlchemyError as e:
            return {
                "error": "Database error occurred while sending reminders.",
                "code": "DB_ERROR",
                "details": str(e)
            }, 500

        except Exception as e:
            return {
                "error": "An unexpected error occurred.",
                "code": "INTERNAL_SERVER_ERROR",
                "details": str(e)
            }, 500
# <-------------------------------------------------------------------------------------------------------------->

# <-------------------------------------SOS--------------------------------------------------------------------->

@sc.route('/send-sos')
class SendSOS(Resource):
    @jwt_required()
    def post(self):
        """Send SOS message from a senior to all mapped caregivers"""
        try:
            user_id = get_jwt_identity()

            # Get the calling user
            senior = User.query.get(user_id)
            if not senior:
                return {
                    "error": "User not found.",
                    "code": "USER_NOT_FOUND"
                }, 404

            # Check user role
            if senior.role != 'senior_citizen':
                return {
                    "error": "Only senior citizens can send SOS alerts.",
                    "code": "FORBIDDEN_ROLE"
                }, 403

            # Find all approved caregiver mappings
            caregiver_mappings = CaregiverSeniorMap.query.filter_by(
                senior_id=user_id,
                status='approved'
            ).all()

            if not caregiver_mappings:
                return {
                    "message": "No caregivers mapped to this user.",
                    "code": "NO_CAREGIVER_FOUND"
                }, 404

            sos_message = f"SOS Alert! {senior.first_name} {senior.last_name} needs immediate assistance!"

            sent_alerts = []
            for mapping in caregiver_mappings:
                caregiver = User.query.get(mapping.caregiver_id)
                if caregiver:
                    # Simulate sending alert
                    print(f"Sending SOS to caregiver {caregiver.username}: {sos_message}")

                    # STORE IN NOTIFICATIONS TABLE
                    notif = Notification(
                        sender_id=senior.id,
                        receiver_id=caregiver.id,
                        type='sos',
                        message=sos_message,
                        medicine_id=None,
                        slot=None
                    )
                    db.session.add(notif)

                    sent_alerts.append({
                        "caregiver_id": caregiver.id,
                        "caregiver_name": f"{caregiver.first_name} {caregiver.last_name}",
                        "message": sos_message
                    })

                    db.session.commit()


            return {
                "status": "SOS sent successfully",
                "alerts_sent": sent_alerts
            }, 200

        except SQLAlchemyError as e:
            return {
                "error": "Database error occurred while sending SOS.",
                "code": "DB_ERROR",
                "details": str(e)
            }, 500

        except Exception as e:
            return {
                "error": "An unexpected error occurred.",
                "code": "INTERNAL_SERVER_ERROR",
                "details": str(e)
            }, 500
    
# <------------------------------------------------------------------------------------------------------------->
@sc.route('/send-poke', methods=['POST'])
class SendPoke(Resource):
    @jwt_required()
    def post(self):
        user = current_user
        data = request.get_json()

        if user.role != 'care_giver':
            return {"error": "Only caregivers can send poke alerts."}, 403

        senior_id = data.get('senior_id')
        medicine_id = data.get('medicine_id')
        slot = data.get('slot')

        if not senior_id or not medicine_id or not slot:
            return {"error": "Missing senior_id, medicine_id, or slot"}, 400

        message = f"💊 Reminder: Take your {slot} medicine"

        notif = Notification(
            sender_id=user.id,
            receiver_id=senior_id,
            type='poke',
            message=message,
            medicine_id=medicine_id,
            slot=slot
        )
        db.session.add(notif)
        db.session.commit()

        return {"status": "Poke alert sent"}, 200

# <-------------------------------------Display all medicines of an elderly and caregiver------------------------------------>
@sc.route('/medicines')
class AllMedicines(Resource):
    @jwt_required()
    def get(self):
        """Get all medicines for logged-in user (senior or caregiver)"""
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)

            if not user:
                return {
                    "error": "User not found.",
                    "code": "USER_NOT_FOUND"
                }, 404

            # Initialize container
            mappings = []

            if user.role == 'senior':
                mappings = UserMedMap.query.filter_by(user_id=user_id).all()

            elif user.role == 'caregiver':
                senior_ids = db.session.query(CaregiverSeniorMap.senior_id).filter_by(
                    caregiver_id=user_id, status='approved'
                ).all()
                senior_ids = [sid[0] for sid in senior_ids]

                if not senior_ids:
                    return {
                        "error": "No senior citizens mapped to this caregiver.",
                        "code": "NO_SENIORS_ASSIGNED"
                    }, 404

                mappings = UserMedMap.query.filter(UserMedMap.user_id.in_(senior_ids)).all()

            else:
                return {
                    "error": "User role not permitted to access medicines.",
                    "code": "FORBIDDEN_ROLE"
                }, 403

            if not mappings:
                return {
                    "message": "No medicines found.",
                    "code": "NO_MEDICINES_FOUND"
                }, 200

            result = []
            for map in mappings:
                med = map.medicine
                assigned_user = map.user

                result.append({
                    "medicine_id": med.id if med else None,
                    "title": med.title if med else "",
                    "description": med.description if med else "",
                    "image": med.image if med else "",
                    "dosage": map.dosage,
                    "start_date": map.start_date.isoformat() if map.start_date else None,
                    "end_date": map.end_date.isoformat() if map.end_date else None,
                    "assigned_to": f"{assigned_user.first_name} {assigned_user.last_name}" if assigned_user else "Unknown"
                })

            return {
                "medicines": result
            }, 200

        except SQLAlchemyError as e:
            return {
                "error": "Database error occurred while fetching medicines.",
                "code": "DB_ERROR",
                "details": str(e)
            }, 500

        except Exception as e:
            return {
                "error": "An unexpected error occurred.",
                "code": "INTERNAL_SERVER_ERROR",
                "details": str(e)
            }, 500

#<------------------------------------------------------------------------------------------------------------->

# <-------------------------------------Senior citizen approve caregiver request------------------------------------>

@sc.route('/approve-caregiver')
class ApproveCaregiver(Resource):
    @jwt_required()
    @sc.expect(sc.model('ApproveCaregiver', {
        'caregiver_id': fields.Integer(required=True, description='ID of the caregiver to approve'),
        'approve': fields.Boolean(required=True, description='True to approve, False to deny')
    }))
    def post(self):
        """Senior approves or denies caregiver connection request"""
        try:
            data = request.get_json()
            caregiver_id = data.get('caregiver_id')
            approve = data.get('approve')

            if caregiver_id is None or approve is None:
                return {
                    "error": "'caregiver_id' and 'approve' are required fields.",
                    "code": "MISSING_FIELDS"
                }, 400

            senior_id = get_jwt_identity()
            senior = User.query.get(senior_id)

            if not senior or senior.role != 'senior_citizen':
                return {
                    "error": "Only senior citizens can approve caregiver requests.",
                    "code": "FORBIDDEN_ROLE"
                }, 403

            relation = CaregiverSeniorMap.query.filter_by(
                caregiver_id=caregiver_id, senior_id=senior_id
            ).first()

            if not relation:
                return {
                    "error": "No pending request found from this caregiver.",
                    "code": "RELATION_NOT_FOUND"
                }, 404

            if relation.status == 'approved' and approve:
                return {
                    "message": "Caregiver request already approved.",
                    "code": "ALREADY_APPROVED"
                }, 200

            relation.status = 'approved' if approve else 'rejected'
            db.session.commit()

            return {
                "message": f"Caregiver request {'approved' if approve else 'rejected'} successfully.",
                "caregiver_id": caregiver_id,
                "status": relation.status
            }, 200

        except SQLAlchemyError as e:
            db.session.rollback()
            return {
                "error": "Database error occurred while processing the caregiver approval.",
                "code": "DB_ERROR",
                "details": str(e)
            }, 500

        except Exception as e:
            return {
                "error": "An unexpected error occurred.",
                "code": "INTERNAL_SERVER_ERROR",
                "details": str(e)
            }, 500

# <------------------------------------------------------------------------------------------------------------->

# <-------------------------------------Caregiver send request to senior citizen------------------------------------>

@sc.route('/request-senior')
class RequestSenior(Resource):
    @jwt_required()
    @sc.expect(sc.model('RequestSenior', {
        'senior_id': fields.Integer(required=True, description="ID of the senior citizen to request")
    }), validate=True)
    def post(self):
        """Caregiver sends a request to a senior citizen"""
        try:
            data = request.get_json()
            senior_id = data.get('senior_id')
            caregiver_id = get_jwt_identity()

            caregiver = User.query.get(caregiver_id)
            if not caregiver or caregiver.role != 'care_giver':
                return {
                    "error": "Only caregivers can send requests.",
                    "code": "FORBIDDEN_ROLE"
                }, 403

            senior = User.query.get(senior_id)
            if not senior or senior.role != 'senior_citizen':
                return {
                    "error": "Target user is not a valid senior citizen.",
                    "code": "INVALID_SENIOR"
                }, 404

            # Check for existing caregiver-senior relationship
            relation = CaregiverSeniorMap.query.filter_by(
                caregiver_id=caregiver_id,
                senior_id=senior_id
            ).first()

            if relation:
                if relation.status == 'pending':
                    return {
                        "message": "Request already sent and pending approval.",
                        "code": "REQUEST_PENDING"
                    }, 200
                elif relation.status == 'approved':
                    return {
                        "message": "You are already approved as a caregiver for this senior.",
                        "code": "ALREADY_APPROVED"
                    }, 200
                elif relation.status == 'rejected':
                    return {
                        "message": "Your previous request was rejected.",
                        "code": "REQUEST_REJECTED"
                    }, 200

            # Create new caregiver-senior relationship
            new_relation = CaregiverSeniorMap(
                caregiver_id=caregiver_id,
                senior_id=senior_id,
                status='pending'
            )
            db.session.add(new_relation)
            db.session.commit()

            return {
                "message": "Request sent to senior citizen successfully.",
                "senior_id": senior_id,
                "status": "pending"
            }, 201

        except SQLAlchemyError as e:
            db.session.rollback()
            return {
                "error": "Database error occurred while creating request.",
                "code": "DB_ERROR",
                "details": str(e)
            }, 500

        except Exception as e:
            return {
                "error": "An unexpected error occurred.",
                "code": "INTERNAL_SERVER_ERROR",
                "details": str(e)
            }, 500
    

# <-------------------------------------Admin approval for new medicines------------------------------------>

@sc.route('/admin/medicine/approval', methods=["POST", "OPTIONS"])
class MedicineApproval(Resource):
    @jwt_required()
    @sc.expect(sc.model('MedicineApproval', {
        'medicine_id': fields.Integer(required=True, description='ID of the medicine to act upon'),
        'approve': fields.Boolean(required=True, description='True to approve, False to reject')
    }), validate=True)
    def post(self):
        """Admin approves or rejects a medicine"""
        try:
            user_id = get_jwt_identity()
            admin = User.query.get(user_id)

            if not admin or admin.role != 'admin':
                return {
                    "error": "Only admins can perform this action.",
                    "code": "FORBIDDEN_ROLE"
                }, 403

            data = request.get_json()
            medicine_id = data.get('medicine_id')
            approve = data.get('approve')

            medicine = Medicine.query.get(medicine_id)
            if not medicine:
                return {
                    "error": "Medicine not found.",
                    "code": "MEDICINE_NOT_FOUND"
                }, 404

            # Handle already final statuses
            if medicine.status == 'approved' and approve:
                return {
                    "error": "Medicine is already approved.",
                    "code": "ALREADY_APPROVED"
                }, 400

            if medicine.status == 'rejected' and not approve:
                return {
                    "error": "Medicine is already rejected.",
                    "code": "ALREADY_REJECTED"
                }, 400

            # Apply approval/rejection
            medicine.status = 'approved' if approve else 'rejected'
            medicine.is_approved = approve

            db.session.commit()

            return {
                "message": f"Medicine has been {medicine.status}.",
                "medicine_id": medicine.id,
                "status": medicine.status,
                "approved": medicine.is_approved
            }, 200

        except SQLAlchemyError as e:
            db.session.rollback()
            return {
                "error": "Database error occurred while updating medicine approval.",
                "code": "DB_ERROR",
                "details": str(e)
            }, 500

        except Exception as e:
            return {
                "error": "An unexpected error occurred.",
                "code": "INTERNAL_SERVER_ERROR",
                "details": str(e)
            }, 500
    def options(self):
        return {}, 200

# <------------------------------------------------------------------------------------------------------------->

# <-------------------------------------List All Pending Medicines------------------------------------>

@sc.route('/admin/medicine/pending', methods=["GET", "OPTIONS"])
class PendingMedicines(Resource):
    @jwt_required()
    def get(self):
        """List all unapproved medicines (admin only)"""
        try:
            user_id = get_jwt_identity()
            admin = User.query.get(user_id)

            if not admin or admin.role != 'admin':
                return {
                    "error": "Only admins can view pending medicines.",
                    "code": "FORBIDDEN_ROLE"
                }, 403

            pending = Medicine.query.filter_by(status="pending").all()

            if not pending:
                return {
                    "message": "No pending medicines found.",
                    "medicines": [],
                    "code": "NO_PENDING_MEDICINES"
                }, 200

            result = [{
                "id": m.id,
                "title": m.title,
                "description": m.description,
                "user_id": m.user_id,
                "created_at": m.created_at.isoformat() if m.created_at else None
            } for m in pending]

            return {
                "medicines": result,   # ✅ uniform
                "count": len(result)
            }, 200


        except SQLAlchemyError as e:
            return {
                "error": "A database error occurred while fetching pending medicines.",
                "code": "DB_ERROR",
                "details": str(e)
            }, 500

        except Exception as e:
            return {
                "error": "An unexpected error occurred.",
                "code": "INTERNAL_SERVER_ERROR",
                "details": str(e)
            }, 500
        
    def options(self):
        return {}, 200 

# <-------------------------------------List All Rejected Medicines------------------------------------>
@sc.route('/admin/medicine/rejected')
class RejectedMedicines(Resource):
    @jwt_required()
    def get(self):
        """List all rejected medicines (admin only)"""
        try:
            user_role = current_user.role

            if user_role != 'admin':
                return {
                    "error": "Only admins can view rejected medicines.",
                    "code": "FORBIDDEN_ROLE"
                }, 403

            rejected = Medicine.query.filter_by(status="rejected").all()

            if not rejected:
                return {
                    "message": "No rejected medicines found.",
                    "rejected_medicines": [],
                    "code": "NO_REJECTED_MEDICINES"
                }, 200

            result = [{
                "id": m.id,
                "title": m.title,
                "description": m.description,
                "user_id": m.user_id,
                "created_at": m.created_at.isoformat() if m.created_at else None
            } for m in rejected]

            return {
                "rejected_medicines": result,
                "count": len(result)
            }, 200

        except SQLAlchemyError as e:
            return {
                "error": "Database error occurred while fetching rejected medicines.",
                "code": "DB_ERROR",
                "details": str(e)
            }, 500

        except Exception as e:
            return {
                "error": "An unexpected error occurred.",
                "code": "INTERNAL_SERVER_ERROR",
                "details": str(e)
            }, 500

 # <------------------------------------------------------------------------------------------------------------->

# <----------------------------------------------------------------------------------------------------->

# <-------------------------------------Upcoming medications------------------------------------>
@sc.route('/upcoming-medications')
class UpcomingMedications(Resource):
    @jwt_required()
    def get(self):
        """Get upcoming medications before scheduled times for the logged-in senior or approved seniors for caregiver"""
        try:
            user = current_user
            now = datetime.now(ZoneInfo("Asia/Kolkata"))
            current_hour = now.hour
            today = now.date()

            # Determine which slots should be shown
            slots = []
            if 4 <= current_hour < 10:
                slots.extend(['breakfast_before', 'breakfast_after'])
            if 10 <= current_hour < 16:
                slots.extend(['lunch_before', 'lunch_after'])
            if 16 <= current_hour < 24:
                slots.extend(['dinner_before', 'dinner_after'])

            if not slots:
                return {
                    "message": "No upcoming medications for the current time window.",
                    "upcoming_medications": [],
                    "code": "NO_ACTIVE_TIME_SLOT"
                }, 200

            result = []

            def get_meds_for_user(user_id):
                return UserMedMap.query.join(Medicine).filter(
                    UserMedMap.user_id == user_id,
                    UserMedMap.start_date <= today,
                    UserMedMap.end_date >= today
                ).all()

            if user.role == 'senior_citizen':
                meds = get_meds_for_user(user.id)
                result = filter_meds_by_time(meds, slots)

            elif user.role == 'care_giver':
                approved_seniors = CaregiverSeniorMap.query.filter_by(
                    caregiver_id=user.id,
                    status="approved"
                ).with_entities(CaregiverSeniorMap.senior_id).all()

                senior_ids = [s[0] for s in approved_seniors]

                if not senior_ids:
                    return {
                        "message": "No senior citizens mapped to this caregiver.",
                        "code": "NO_SENIORS_ASSIGNED",
                        "upcoming_medications": []
                    }, 200

                for sid in senior_ids:
                    meds = get_meds_for_user(sid)
                    result.extend(filter_meds_by_time(meds, slots, sid))

            else:
                return {
                    "error": "You are not authorized to access this resource.",
                    "code": "UNAUTHORIZED_ROLE"
                }, 403

            if not result:
                return {
                    "message": "No upcoming medications found.",
                    "code": "NO_UPCOMING_MEDICATIONS"
                }, 200

            return {
                "upcoming_medications": result,
                "count": len(result)
            }, 200

        except SQLAlchemyError as e:
            return {
                "error": "A database error occurred while fetching upcoming medications.",
                "code": "DB_ERROR",
                "details": str(e)
            }, 500
        except Exception as e:
            return {
                "error": "An unexpected error occurred.",
                "code": "INTERNAL_SERVER_ERROR",
                "details": str(e)
            }, 500
        
def filter_meds_by_time(meds, valid_slots, user_id=None):
    """Filter medicine slots by upcoming 3-hour window, excluding marked as taken"""
    upcoming = []
    today_utc = datetime.utcnow().date()

    for med in meds:
        #  Skip expired meds
        if med.end_date and med.end_date < today_utc:
            continue
        today_status = Status.query.filter(
            Status.user_med_map_id == med.id,
            func.date(Status.date) == today_utc
        ).first()

        if not today_status:
            today_status = Status(
                user_med_map_id=med.id,
                date=today_utc,
                breakfast_before=False if med.breakfast_before else None,
                breakfast_after=False if med.breakfast_after else None,
                lunch_before=False if med.lunch_before else None,
                lunch_after=False if med.lunch_after else None,
                dinner_before=False if med.dinner_before else None,
                dinner_after=False if med.dinner_after else None
            )
            db.session.add(today_status)
            db.session.commit()
        for slot in valid_slots:
            if getattr(med, slot, False):
                status_entry=Status.query.filter(
                        Status.user_med_map_id == med.id,
                        func.date(Status.date) == today_utc,
                        getattr(Status, slot) == True
                    ).first()
                if status_entry:
                    continue  # Skip this taken slot only

                upcoming.append({
                    "user_id": user_id,
                    "medicine_id": med.medicine_id,
                    "medicine_title": med.medicine.title,
                    "dosage": med.dosage,
                    "start_date": med.start_date.isoformat(),
                    "end_date": med.end_date.isoformat(),
                    "reminder_slot": slot.replace('_', ' ').capitalize()
                })
    return upcoming


# <-------------------------------------Today's medication for Senior Citizen------------------------------------>

@sc.route('/todays-medications')
class TodaysMedications(Resource):
    @jwt_required()
    def get(self):
        """Get today's medications for the logged-in senior citizen or all approved seniors for caregiver"""
        try:
            user = current_user
            today = datetime.utcnow().date()
            result = []

            def fetch_grouped_assignments(uid):
                """Get today's meds for a user_id, grouping slots per medicine & category"""
                assignments = UserMedMap.query.filter(
                    UserMedMap.user_id == uid,
                    UserMedMap.start_date <= today,
                    UserMedMap.end_date >= today
                ).all()

                meds_dict = {}  

                for assign in assignments:
                    med = assign.medicine
                    if not med:
                        continue

                    # Define slots with category (daytime or nighttime)
                    slots_info = [
                        ("Before Breakfast", assign.breakfast_before, "daytime"),
                        ("After Breakfast", assign.breakfast_after, "daytime"),
                        ("Before Lunch", assign.lunch_before, "daytime"),
                        ("After Lunch", assign.lunch_after, "daytime"),
                        ("Before Dinner", assign.dinner_before, "nighttime"),
                        ("After Dinner", assign.dinner_after, "nighttime")
                    ]

                    for slot_name, is_active, category in slots_info:
                        if is_active:
                            key = (assign.medicine_id, category)
                            if key not in meds_dict:
                                meds_dict[key] = {
                                    "user_id": uid,
                                    "medicine_name": med.title,
                                    "dosage": assign.dosage,
                                    "category": category,
                                    "times": []  
                                }
                            meds_dict[key]["times"].append(slot_name)

                return list(meds_dict.values())

            if user.role == 'senior_citizen':
                result = fetch_grouped_assignments(user.id)

            elif user.role == 'care_giver':
                approved_seniors = CaregiverSeniorMap.query.filter_by(
                    caregiver_id=user.id,
                    status="approved"
                ).with_entities(CaregiverSeniorMap.senior_id).all()
                senior_ids = [s[0] for s in approved_seniors]
                if not senior_ids:
                    return {
                        "message": "No senior citizens mapped to this caregiver.",
                        "medications": [],
                        "code": "NO_SENIORS_ASSIGNED"
                    }, 200

                for sid in senior_ids:
                    result.extend(fetch_grouped_assignments(sid))
            else:
                return {
                    "error": "You are not authorized to access this resource.",
                    "code": "UNAUTHORIZED_ROLE"
                }, 403

            if not result:
                return {
                    "message": "No medications scheduled for today.",
                    "medications": [],
                    "code": "NO_TODAYS_MEDICINES"
                }, 200

            return {
                "date": today.isoformat(),
                "medications": result,
                "count": len(result)
            }, 200

        except SQLAlchemyError as e:
            return {
                "error": "Database error while fetching today’s medications.",
                "code": "DB_ERROR",
                "details": str(e)
            }, 500
        except Exception as e:
            return {
                "error": "An unexpected error occurred.",
                "code": "INTERNAL_SERVER_ERROR",
                "details": str(e)
            }, 500

# <------------------------------------------------------------------------------------------------------------->

# <-------------------------------------Marking Medicines as taken------------------------------------>

@sc.route("/mark-medicine-taken", methods=["PUT"])
class MarkMedicineTaken(Resource):
    @jwt_required()
    @sc.expect(sc.model('MarkMedicineTaken', {
        'medicine_id': fields.Integer(required=True),
        'slot': fields.String(required=True, example="breakfast_before"),
    }), validate=True)
    def put(self):
        """Mark a medicine as taken for the logged-in senior citizen"""
        user_id = get_jwt_identity()
        data = request.get_json()
        
        medicine_id = data.get("medicine_id")
        slot = data.get("slot")  
        if not all([medicine_id, slot]):
            return {"error": "medicine_id and slot are required."}, 400

        if slot not in [
            "breakfast_before", "breakfast_after",
            "lunch_before", "lunch_after",
            "dinner_before", "dinner_after"
        ]:
            return {"error": "Invalid slot value."}, 400

        user_med_map = UserMedMap.query.filter_by(user_id=user_id,medicine_id=medicine_id).first()
        if not user_med_map:
            return {"error": "Medicine assignment not found."}, 404
        status = Status.query.filter(Status.user_med_map_id==user_med_map.id,func.date(Status.date)==datetime.utcnow().date()).first()
        if not status:
            return {"error": "Status entry not found for this date."}, 404
        setattr(status, slot, True)
        try:
            db.session.commit()
            return {"message": f"Marked {slot} as taken for {datetime.utcnow().date()}"}, 200
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

# <------------------------------------------------------------------------------------------------------------->

# <-------------------------------------Daily Health Entry------------------------------------>

@sc.route("/health-entry", methods=["POST"])
class HealthEntry(Resource):
    @jwt_required()
    @sc.expect(sc.model('HealthEntry', {
        'bp_systolic': fields.Integer(required=True),
        'bp_diastolic': fields.Integer(required=True),
        'sugar_level': fields.Float(required=True),
        'senior_id': fields.Integer(required=False)  # Optional for caregiver role
    }), validate=True)
    def post(self):
        """Record a daily health entry for the logged-in senior citizen or a caregiver for their senior"""
        user_id = get_jwt_identity()
        user_role = current_user.role
        data = request.get_json()

        if user_role == 'care_giver' and 'senior_id' in data:
            senior_id = data['senior_id']
        elif user_role == 'senior_citizen':
            senior_id = user_id  # Use the logged-in senior citizen's ID
        else:
            return {"error": "Unauthorized action."}, 403

        try:
            today = datetime.utcnow().date()  
            existing_entry = DailyHealthEntry.query.filter_by(user_id=senior_id).filter(func.date(DailyHealthEntry.date) == today).first()  # Compare the date part only
            
            if existing_entry:
                existing_entry.bp_systolic = data.get("bp_systolic")
                existing_entry.bp_diastolic = data.get("bp_diastolic")
                existing_entry.sugar_level = data.get("sugar_level")
                db.session.commit()
                return {"message": "Today's health entry updated successfully."}, 201
            new_entry = DailyHealthEntry(
                user_id=senior_id,
                date=today,
                bp_systolic=data.get("bp_systolic"),
                bp_diastolic=data.get("bp_diastolic"),
                sugar_level=data.get("sugar_level")
            )
            db.session.add(new_entry)
            db.session.commit()
            return {"message": "Today's health entry recorded successfully."}, 201
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

# <------------------------------------------------------------------------------------------------------------->

@sc.route('/my-caregiver')
@sc.doc(description="Fetches the caregiver information for a senior citizen.")
class MyCaregiver(Resource):
    @jwt_required()
    def get(self):
        """Fetches the caregiver information for a senior citizen."""
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if user.role != "senior_citizen":
            return {"error": "Unauthorized"}, 403
        # Get mapping with approved status
        map = CaregiverSeniorMap.query.filter_by(senior_id=user_id, status='approved').first()
        if not map:
            return {"caregiver": None}, 200

        caregiver = User.query.get(map.caregiver_id)
        return {
            "caregiver": {
                "firstName": caregiver.first_name,
                "lastName": caregiver.last_name,
                "username": caregiver.username
            }
        }, 200

@sc.route('/my-dependents')
@sc.doc(description="Retrieves all approved senior citizens (dependents) assigned to the logged-in caregiver.")
class MyDependents(Resource):
    @jwt_required()
    def get(self):
        """Retrieves all approved senior citizens (dependents) assigned to the logged-in caregiver."""
        user_id = get_jwt_identity()
        user_role = current_user.role
        if user_role != 'care_giver':
            return {"error": "You are not authorized to access this resource."}, 403

        # Get all approved seniors linked to this caregiver
        mappings = CaregiverSeniorMap.query.filter_by(caregiver_id=user_id, status='approved').all()
        dependents = []
        for m in mappings:
            senior = User.query.get(m.senior_id)
            if senior:
                dependents.append({
                    "id": senior.id,
                    "firstName": senior.first_name,
                    "lastName": senior.last_name,
                    "username": senior.username,
                    "role": senior.role
                })

        return {"dependents": dependents}, 200

@sc.route('/delete-dependent')
@sc.doc(description="Delete or unassign a dependent (approved senior citizen) from the logged-in caregiver.")
class DeleteDependent(Resource):
    @jwt_required()
    @sc.expect(sc.model('DeleteDependent', {
        'senior_id': fields.Integer(required=True, description='ID of the senior to remove as dependent')
    }), validate=True)
    def delete(self):
        """Delete an approved senior (dependent) from caregiver's assigned list"""
        try:
            caregiver_id = get_jwt_identity()
            caregiver = User.query.get(caregiver_id)

            if not caregiver or caregiver.role != 'care_giver':
                return {
                    "error": "You are not authorized to perform this action.",
                    "code": "FORBIDDEN_ROLE"
                }, 403

            data = request.get_json()
            senior_id = data.get('senior_id')

            if not senior_id:
                return {
                    "error": "Missing 'senior_id' in request body.",
                    "code": "MISSING_SENIOR_ID"
                }, 400

            # Find the existing caregiver–senior relation
            mapping = CaregiverSeniorMap.query.filter_by(
                caregiver_id=caregiver_id,
                senior_id=senior_id,
                status='approved'
            ).first()

            if not mapping:
                return {
                    "error": "No approved dependent found with the given senior ID.",
                    "code": "DEPENDENT_NOT_FOUND"
                }, 404

            # Delete the mapping (or update status to 'removed' for soft deletion)
            db.session.delete(mapping)
            db.session.commit()

            return {
                "message": "Dependent removed successfully.",
                "senior_id": senior_id
            }, 200

        except SQLAlchemyError as e:
            db.session.rollback()
            return {
                "error": "A database error occurred while removing the dependent.",
                "code": "DB_ERROR",
                "details": str(e)
            }, 500

        except Exception as e:
            return {
                "error": "An unexpected error occurred.",
                "code": "INTERNAL_SERVER_ERROR",
                "details": str(e)
            }, 500

from datetime import date, timedelta

@sc.route('/user-stats/<int:senior_id>')
@sc.doc(description="Returns medicine compliance and vital statistics.")
class UserStats(Resource):
    @jwt_required()
    def get(self, senior_id):
        """Returns medicine compliance and vital statistics."""
        uid = get_jwt_identity()
        me = User.query.get(uid)
        slot_times = {
    "breakfast_before": (4, 10),
    "breakfast_after": (4, 10),
    "lunch_before": (10, 16),
    "lunch_after": (10, 16),
    "dinner_before": (16, 23),
    "dinner_after": (16, 23)
}

        # Role-based access control
        if me.role == 'care_giver':
            mapping = CaregiverSeniorMap.query.filter_by(
                caregiver_id=uid, senior_id=senior_id, status='approved'
            ).first()
            if not mapping:
                return {"error": "Access denied"}, 403
        elif me.role != 'senior_citizen' or me.id != senior_id:
            return {"error": "Access denied"}, 403

        today = date.today()
        last_30_excluding_today = today - timedelta(days=30)

        meds = UserMedMap.query.filter_by(user_id=senior_id).all()
        stacked = {}

        for um in meds:
            name = um.medicine.title
            stacked.setdefault(name, {"taken": 0, "missed": 0, "total_assigned": 0})

            for s in um.statuses:
                status_date = s.date.date()
                if last_30_excluding_today <= status_date <= today:
                    for slot_name, slot_val in [
                        ("breakfast_before", s.breakfast_before),
                        ("breakfast_after", s.breakfast_after),
                        ("lunch_before", s.lunch_before),
                        ("lunch_after", s.lunch_after),
                        ("dinner_before", s.dinner_before),
                        ("dinner_after", s.dinner_after)
                    ]:
                        if slot_val is not None:
                            stacked[name]["total_assigned"] += 1
                            if slot_val:
                                stacked[name]["taken"] += 1
                            else:
                                stacked[name]["missed"] += 1


        # Vitals: last 7 days INCLUDING today
        vitals_start = today - timedelta(days=6) 
        entries = DailyHealthEntry.query.filter(
            DailyHealthEntry.user_id == senior_id,
            DailyHealthEntry.date >= vitals_start
        ).order_by(DailyHealthEntry.date).all()

        days = [e.date.strftime('%b %d') for e in entries]
        systolic = [e.bp_systolic for e in entries]
        diastolic = [e.bp_diastolic for e in entries]
        sugar = [e.sugar_level for e in entries]

        return {
            "medicineCompliance": {
                "labels": list(stacked.keys()),
                "taken": [v["taken"] for v in stacked.values()],
                "missed": [v["missed"] for v in stacked.values()]
            },
            "vitalsLast7": {
                "labels": days,
                "systolic": systolic,
                "diastolic": diastolic,
                "sugar": sugar
            }
        }, 200
    
# <------------------------Search system users not already assigned as dependents to the current caregiver------------>
@sc.route('/search-users')
@sc.doc(params={"query": "Search query for username or full name"})
class SearchUsers(Resource):
    @jwt_required()
    def get(self):
        """Search system users not already assigned as dependents to the current caregiver"""
        try:
            user = current_user
            if user.role != 'care_giver':
                return {
                    "error": "Only caregivers can search users.",
                    "code": "FORBIDDEN_ROLE"
                }, 403

            query = request.args.get('query', '').strip().lower()
            if not query:
                return {"users": []}, 200

            # Get IDs of all seniors already assigned
            assigned_ids = db.session.query(CaregiverSeniorMap.senior_id).filter_by(
                caregiver_id=user.id
            ).all()
            assigned_ids = [sid[0] for sid in assigned_ids]

            # Search all senior users, excluding already assigned
            matching_users = User.query.filter(
                User.role == 'senior_citizen',
                ~User.id.in_(assigned_ids),
                (
                    func.lower(User.username).contains(query) |
                    ((User.first_name + ' ' + User.last_name).ilike(f"%{query}%"))
                )
            ).all()

            result = [{
                "id": u.id,
                "username": u.username,
                "firstName": u.first_name,
                "lastName": u.last_name
            } for u in matching_users]

            return {"users": result}, 200

        except Exception as e:
            return {
                "error": "An unexpected error occurred.",
                "code": "INTERNAL_SERVER_ERROR",
                "details": str(e)
            }, 500
# <------------------------------------------------------------------------------>

# <------------------------Add a new dependent to the current caregiver------------>

@sc.route('/add-dependent')
@sc.doc(description="Caregiver adds a new senior citizen as a dependent.")
class AddDependent(Resource):
    @jwt_required()
    @sc.expect(sc.model('AddDependent', {
        'senior_id': fields.Integer(required=True, description="ID of the senior to be added")
    }), validate=True)
    def post(self):
        """Add a senior citizen as a dependent for the logged-in caregiver"""
        try:
            caregiver = current_user

            if caregiver.role != 'care_giver':
                return {
                    "error": "Only caregivers can add dependents.",
                    "code": "FORBIDDEN_ROLE"
                }, 403

            data = request.get_json()
            senior_id = data.get('senior_id')
            if not senior_id:
                return {
                    "error": "'senior_id' is required.",
                    "code": "MISSING_FIELD"
                }, 400

            # Check for existing relation
            existing = CaregiverSeniorMap.query.filter_by(
                caregiver_id=caregiver.id,
                senior_id=senior_id
            ).first()

            if existing:
                return {
                    "success": False,
                    "code": "ALREADY_DEPENDENT",
                    "message": "User is already a dependent or has a pending request."
                }, 200

            # Create new mapping
            new_relation = CaregiverSeniorMap(
                caregiver_id=caregiver.id,
                senior_id=senior_id,
                status='approved'  # You can change to 'pending' if approval is needed
            )
            db.session.add(new_relation)
            db.session.commit()

            senior = User.query.get(senior_id)
            return {
                "success": True,
                "dependent": {
                    "id": senior.id,
                    "username": senior.username,
                    "firstName": senior.first_name,
                    "lastName": senior.last_name
                }
            }, 201

        except SQLAlchemyError as e:
            db.session.rollback()
            return {
                "error": "Database error occurred while adding dependent.",
                "code": "DB_ERROR",
                "details": str(e)
            }, 500

        except Exception as e:
            return {
                "error": "An unexpected error occurred.",
                "code": "INTERNAL_SERVER_ERROR",
                "details": str(e)
            }, 500
# <------------------------------------------------------------------------------>


#<------------------------Dependent Profile APIs------------------------------------>

@sc.route('/dependent/<int:senior_id>/details')
@sc.doc(description="Get details of a dependent or senior's own profile.")
class DependentDetails(Resource):
    @jwt_required()
    def get(self, senior_id):
        """Get details of a dependent or the senior's own profile"""
        user = current_user

        if user.role == 'care_giver':
            relation = CaregiverSeniorMap.query.filter_by(
                caregiver_id=user.id,
                senior_id=senior_id,
                status='approved'
            ).first()
            if not relation:
                return {"error": "This dependent is not assigned to you."}, 403

        elif user.role == 'senior_citizen':
            if user.id != senior_id:
                return {"error": "You can only view your own profile."}, 403

        else:
            return {"error": "Access denied"}, 403

        senior = User.query.get(senior_id)
        if not senior:
            return {"error": "User not found."}, 404

        return {
            "id": senior.id,
            "firstName": senior.first_name,
            "lastName": senior.last_name,
            "username": senior.username
        }, 200


# <------------------------Get medications for a dependent------------------------>
@sc.route('/dependent/<int:senior_id>/medications')
@sc.doc(description="Get medications for a dependent or senior's own medications.")
class DependentMedications(Resource):
    @jwt_required()
    def get(self, senior_id):
        """Get medications for a dependent or for senior's own profile"""
        user = current_user

        if user.role == 'care_giver':
            mapping_exists = CaregiverSeniorMap.query.filter_by(
                caregiver_id=user.id,
                senior_id=senior_id,
                status='approved'
            ).first()
            if not mapping_exists:
                return {"error": "Unauthorized assignment"}, 403

        elif user.role == 'senior_citizen':
            if user.id != senior_id:
                return {"error": "You can only view your own medications."}, 403

        else:
            return {"error": "Access denied"}, 403

        # Fetch medicines
        meds = UserMedMap.query.filter_by(user_id=senior_id).all()
        result = []
        for um in meds:
            med = um.medicine
            result.append({
                "id": um.id,
                "medicineTitle": med.title,
                "dosage": um.dosage,
                "startDate": um.start_date.isoformat(),
                "endDate": um.end_date.isoformat() if um.end_date else None,
                "breakfast_before": um.breakfast_before,
                "breakfast_after": um.breakfast_after,
                "lunch_before": um.lunch_before,
                "lunch_after": um.lunch_after,
                "dinner_before": um.dinner_before,
                "dinner_after": um.dinner_after
            })

        return {"medications": result}, 200

# <------------------------Delete a medication mapping------------------------>
@sc.route('/medication/<int:map_id>', methods=['DELETE'])
@sc.doc(description="Delete a medication mapping.")
class DeleteMedicineMapping(Resource):
    @jwt_required()
    def delete(self, map_id):
        """Delete a medication mapping"""
        med_mapping = UserMedMap.query.get(map_id)
        if not med_mapping:
            return {"error": "Mapping not found."}, 404

        user = current_user

        # Caregiver can delete if mapped & approved to senior who owns this medication
        if user.role == 'care_giver':
            relation = CaregiverSeniorMap.query.filter_by(
                caregiver_id=user.id,
                senior_id=med_mapping.user_id,
                status='approved'
            ).first()
            if not relation:
                return {"error": "You are not authorized to delete this medication."}, 403

        # Senior citizen can delete only their own medications
        elif user.role == 'senior_citizen':
            if med_mapping.user_id != user.id:
                return {"error": "You can only delete your own medications."}, 403

        else:
            return {"error": "Access denied."}, 403

        db.session.delete(med_mapping)
        db.session.commit()

        return {"message": "Medication deleted"}, 200


# <------------------------Add medication to a dependent------------------------>
@sc.route('/dependent/<int:senior_id>/add-medication', methods=['POST'])
@sc.doc(description="Add medication to a dependent.")
class AddMedicationToUser(Resource):
    @jwt_required()
    def post(self, senior_id):
        """Add medication to a dependent"""
        try:
            data = request.get_json()
            print("🌐 Received POST body:", data)

            if not data or not isinstance(data, dict):
                return {"error": "Invalid JSON payload"}, 400

            # Required field validation
            required_fields = ['medicine_id', 'dosage', 'start_date']
            missing = [f for f in required_fields if f not in data]
            if missing:
                return {"error": f"Missing field(s): {', '.join(missing)}"}, 400

            # Parse start_date
            try:
                start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
            except ValueError:
                return {"error": "Invalid start_date format, expected YYYY-MM-DD"}, 400

            # Parse optional end_date
            end_date = None
            if data.get('end_date'):
                try:
                    end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
                except ValueError:
                    return {"error": "Invalid end_date format, expected YYYY-MM-DD"}, 400

            # Validate end_date ≥ start_date
            if end_date and end_date < start_date:
                return {"error": "End date cannot be before start date."}, 400

            # Validate dosage is a string or number
            dosage = data['dosage']
            if not isinstance(dosage, (str, int, float)) or len(str(dosage).strip()) == 0:
                return {"error": "Invalid dosage"}, 400

            # Validate user role
            caregiver = current_user
            if caregiver.role != 'care_giver':
                return {"error": "Only caregivers can assign medications."}, 403

            # Confirm caregiver-senior assignment
            relation = CaregiverSeniorMap.query.filter_by(
                caregiver_id=caregiver.id,
                senior_id=senior_id,
                status='approved'
            ).first()

            if not relation:
                return {"error": "You are not authorized to modify this dependent."}, 403
            
            medicine_name = Medicine.query.get(data['medicine_id'])

            # Create and save UserMedMap entry
            med_mapping = UserMedMap(
                user_id=senior_id,
                medicine_id=data['medicine_id'],
                dosage=dosage,
                start_date=start_date,
                end_date=end_date or start_date,
                breakfast_before=data.get('breakfast_before', False),
                breakfast_after=data.get('breakfast_after', False),
                lunch_before=data.get('lunch_before', False),
                lunch_after=data.get('lunch_after', False),
                dinner_before=data.get('dinner_before', False),
                dinner_after=data.get('dinner_after', False)
            )
            db.session.add(med_mapping)
            db.session.commit()

            return {
                "success": True,
                "message": "Medication assigned successfully",
                "medication": {
                    "id": med_mapping.id,
                    "medicine_id": med_mapping.medicine_id,
                    "medicineTitle":medicine_name.title,
                    "dosage": med_mapping.dosage,
                    "start_date": med_mapping.start_date.isoformat(),
                    "end_date": med_mapping.end_date.isoformat(),
                    "breakfast_before": med_mapping.breakfast_before,
                    "breakfast_after": med_mapping.breakfast_after,
                    "lunch_before": med_mapping.lunch_before,
                    "lunch_after": med_mapping.lunch_after,
                    "dinner_before": med_mapping.dinner_before,
                    "dinner_after": med_mapping.dinner_after
                }
            }, 201

        except Exception as e:
            db.session.rollback()
            traceback.print_exc()
            return {
                "error": "An unexpected error occurred.",
                "details": str(e)
            }, 500

# <------------------------Music API Endpoints------------------------>
@sc.route('/my-music')
@sc.doc(description="Get the music playlist for the current user.") 
class MyMusic(Resource):
    @jwt_required()
    def get(self):
        """Get the music playlist for the current user."""
        try:
            user = current_user
            if user.role != 'senior_citizen':
                return {"error": "Only senior citizens can access this resource."}, 403

            # Sample playlist
            playlist = [
                {
                    "id": 1,
                    "title": "Memories",
                    "artist": "Bensound",
                    "url": "https://www.bensound.com/bensound-music/bensound-memories.mp3",
                    "cover": "https://i.ytimg.com/vi/zi_oR296950/hqdefault.jpg"
                },
                {
                    "id": 2,
                    "title": "Energy",
                    "artist": "Bensound",
                    "url": "https://www.bensound.com/bensound-music/bensound-energy.mp3",
                    "cover": "https://i1.sndcdn.com/artworks-B7MF52qXlsrbOro7-fVz7RQ-t500x500.jpg"
                },
                {
                    "id": 3,
                    "title": "A New Beginning",
                    "artist": "Bensound",
                    "url": "https://www.bensound.com/bensound-music/bensound-anewbeginning.mp3",
                    "cover": "https://i.ytimg.com/vi/MN5vSCdnqII/maxresdefault.jpg"
                },
                
            ]

            return {"tracks": playlist}, 200

        except Exception as e:
            return {
                "error": "Failed to load music playlist.",
                "details": str(e)
            }, 500
            
@sc.route('/pending-caregiver-requests')
class PendingCaregiverRequests(Resource):
    @jwt_required()
    def get(self):
        """Get all pending caregiver requests for the senior citizen"""
        try:
            senior_id = get_jwt_identity()
            senior = User.query.get(senior_id)

            if not senior or senior.role != 'senior_citizen':
                return {
                    "error": "Only senior citizens can view caregiver requests.",
                    "code": "FORBIDDEN_ROLE"
                }, 403

            pending_relations = CaregiverSeniorMap.query.filter_by(
                senior_id=senior_id,
                status='pending'
            ).all()

            result = []
            for rel in pending_relations:
                caregiver = User.query.get(rel.caregiver_id)
                if caregiver:
                    result.append({
                        "caregiver_id": caregiver.id,
                        "caregiver_name": f"{caregiver.first_name} {caregiver.last_name}",
                        "caregiver_username": f"{caregiver.username}"
                    })

            return {"requests": result}, 200

        except Exception as e:
            return {
                "error": "An error occurred while fetching pending requests.",
                "details": str(e),
                "code": "INTERNAL_SERVER_ERROR"
            }, 500
@sc.route('/notifications', methods=['GET'])
class UserNotifications(Resource):
    @jwt_required()
    def get(self):
        user = current_user
        output = []

        # 1. SENIOR CITIZEN — caregiver requests + poke alerts
        if user.role == 'senior_citizen':
            # Pending caregiver requests
            pending_requests = CaregiverSeniorMap.query.filter_by(
                senior_id=user.id, status='pending'
            ).all()
            for req in pending_requests:
                caregiver = User.query.get(req.caregiver_id)
                output.append({
                    "type": "caregiver_request",
                    "message": f"Caregiver request from {caregiver.username}",
                    "caregiver_id": caregiver.id,
                    "caregiver_username": caregiver.username
                })

            # Poke alerts
            pokes = Notification.query.filter_by(
                receiver_id=user.id, type='poke',is_read=False
            ).order_by(Notification.created_at.desc()).all()
            for p in pokes:
                sender = User.query.get(p.sender_id)
                output.append({
                    "id":p.id,
                    "type": "poke",
                    "message": p.message,
                    "from": sender.username,
                    "medicine_title": p.medicine.title if p.medicine else None,
                    "slot": p.slot
                })

        # 2. CAREGIVER — sos alerts
        elif user.role == 'care_giver':
            sos_alerts = Notification.query.filter_by(
                receiver_id=user.id, type='sos',is_read=False
            ).order_by(Notification.created_at.desc()).all()
            for s in sos_alerts:
                sender = User.query.get(s.sender_id)
                output.append({
                    "id":s.id,
                    "type": "sos",
                    "message": s.message,
                    "from": sender.username
                })

        return {
            "count": len(output),
            "notifications": output
        }, 200
@sc.route('/notifications/<int:notif_id>/read', methods=['PUT'])
class MarkNotificationRead(Resource):
    @jwt_required()
    def put(self, notif_id):
        user = current_user
        notif = Notification.query.get(notif_id)

        if not notif or notif.receiver_id != user.id:
            return {"error": "Notification not found"}, 404

        notif.is_read = True
        db.session.commit()

        return {"message": "Notification marked as read"}, 200
