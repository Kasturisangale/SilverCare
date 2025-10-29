<template>
  <div
    class="music-player-container"
    :style="containerStyle"
    @mousedown="startDragging"
  >
    <audio
      ref="audioRef"
      :src="currentTrack.url"
      @timeupdate="updateTime"
      @ended="handleTrackEnd"
      @loadedmetadata="setDuration"
      :volume="volume"
    ></audio>

    <div v-if="isCollapsed" class="music-player-collapsed" @click="toggleCollapse">
      <div class="song-info-collapsed">
        <img :src="currentTrack.cover || defaultCover" alt="Album Art" class="collapsed-album-art">
        <div class="text-info">
          <p class="song-title">{{ currentTrack.title }}</p>
          <p class="song-artist">{{ currentTrack.artist }}</p>
        </div>
      </div>
      <div class="controls-collapsed">
        <button class="control-btn" @click.stop="prevTrack" title="Previous">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="19 20 9 12 19 4 19 20"></polygon><line x1="5" y1="19" x2="5" y2="5"></line></svg>
        </button>
        <button class="control-btn" @click.stop="togglePlay" title="Play/Pause">
          <svg v-if="!isPlaying" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" stroke-width="1"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
          <svg v-else xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" stroke-width="1"><rect x="6" y="4" width="4" height="16"></rect><rect x="14" y="4" width="4" height="16"></rect></svg>
        </button>
        <button class="control-btn" @click.stop="nextTrack" title="Next">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="5 4 15 12 5 20 5 4"></polygon><line x1="19" y1="5" x2="19" y2="19"></line></svg>
        </button>
      </div>
    </div>

    <div v-else class="music-player-card">
      <div class="close-btn-container">
        <button class="close-btn" @click="toggleCollapse">
          <svg class="up-arrow" xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 15L12 9L6 15"/></svg>
        </button>
      </div>
      <div v-if="error" class="error-state">
        <p>Could not load music.</p>
        <p class="error-message">{{ error }}</p>
      </div>

      <template v-if="playlist.length > 0">
        <div class="album-art-container">
          <img :src="currentTrack.cover || defaultCover" alt="Album Art" class="album-art" :class="{ 'playing': isPlaying }">
        </div>

        <div class="song-info">
          <h3 class="song-title">{{ currentTrack.title }}</h3>
          <p class="song-artist">{{ currentTrack.artist }}</p>
        </div>

        <div class="progress-container" @click="seekAudio">
          <div class="progress-bar" :style="{ width: progressBarWidth }"></div>
        </div>
        <div class="time-display">
          <span>{{ formatTime(currentTime) }}</span>
          <span>{{ formatTime(duration) }}</span>
        </div>

        <div class="controls">
          <button class="control-btn" @click="prevTrack" title="Previous">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="19 20 9 12 19 4 19 20"></polygon><line x1="5" y1="19" x2="5" y2="5"></line></svg>
          </button>
          <button class="control-btn play-pause-btn" @click="togglePlay">
            <svg v-if="!isPlaying" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" stroke-width="1"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" stroke-width="1"><rect x="6" y="4" width="4" height="16"></rect><rect x="14" y="4" width="4" height="16"></rect></svg>
          </button>
          <button class="control-btn" @click="nextTrack" title="Next">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="5 4 15 12 5 20 5 4"></polygon><line x1="19" y1="5" x2="19" y2="19"></line></svg>
          </button>
        </div>

        <div class="secondary-controls">
            <button :class="['control-btn', 'small-btn', { 'active': isRepeating }]" @click="toggleRepeat" title="Repeat">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="17 1 21 5 17 9"></polyline><path d="M3 11V9a4 4 0 0 1 4-4h14"></path><polyline points="7 23 3 19 7 15"></polyline><path d="M21 13v2a4 4 0 0 1-4 4H3"></path></svg>
            </button>
            <div class="volume-control">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon><path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"></path></svg>
              <input type="range" min="0" max="1" step="0.01" v-model="volume" @input="changeVolume" />
            </div>
            <button :class="['control-btn', 'small-btn', { 'active': isShuffle }]" @click="toggleShuffle" title="Shuffle">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="16 3 21 3 21 8"></polyline><line x1="4" y1="20" x2="21" y2="3"></line><polyline points="16 17 21 17 21 22"></polyline><line x1="4" y1="14" x2="11" y2="7"></line></svg>
            </button>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, onUnmounted } from 'vue';
import apiService from '@/services/apiService';

// --- Refs and State ---
const audioRef = ref(null);
const playlist = ref([]);
const error = ref(null);
const defaultCover = 'https://placehold.co/300x300/e0e0e0/757575?text=Music';
const activeIndex = ref(0);

const isPlaying = ref(false);
const isShuffle = ref(false);
const isRepeating = ref(false);
const isCollapsed = ref(true);

const currentTime = ref(0);
const duration = ref(0);
const volume = ref(Number(localStorage.getItem('music-volume')) || 0.7);

// --- Draggable State ---
const isDragging = ref(false);
const initialX = ref(0);
const initialY = ref(0);
const offsetX = ref(0);
const offsetY = ref(0);
// Persist position in local storage
const storedX = Number(localStorage.getItem('player-x')) || window.innerWidth - 370;
const storedY = Number(localStorage.getItem('player-y')) || window.innerHeight - 100;

const x = ref(storedX);
const y = ref(storedY);

// --- Computed Properties ---
const currentTrack = computed(() => playlist.value[activeIndex.value] || {});
const progressBarWidth = computed(() => {
  if (duration.value === 0) return '0%';
  return `${(currentTime.value / duration.value) * 100}%`;
});

const containerStyle = computed(() => {
  const playerWidth = isCollapsed.value ? 350 : 300;
  const horizontalPadding = isCollapsed.value ? 2 * 16 : 2 * 24;
  const totalWidth = playerWidth + horizontalPadding;
  
  const playerHeight = isCollapsed.value ? 80 : 400; // Estimated expanded height
  const verticalPadding = isCollapsed.value ? 2 * 8 : 2 * 24;
  const totalHeight = playerHeight + verticalPadding;
  
  const clampedX = Math.max(0, Math.min(window.innerWidth - totalWidth, x.value));
  const clampedY = Math.max(0, Math.min(window.innerHeight - totalHeight, y.value));

  // Use CSS transform for positioning for better performance
  return {
    position: 'fixed',
    top: '0',
    left: '0',
    transform: `translate(${clampedX}px, ${clampedY}px)`,
    cursor: isDragging.value ? 'grabbing' : 'grab',
    zIndex: 1000,
    transition: 'transform 0.3s ease',
  };
});


// --- API Fetching ---
async function fetchPlaylist() {
  try {
    const res = await apiService.get('/sc/my-music');
    if (!res.data.tracks || res.data.tracks.length === 0) {
        throw new Error("No tracks found in the playlist.");
    }
    playlist.value = res.data.tracks;
    activeIndex.value = 0;
  } catch (err) {
    console.error('🔴 Failed to fetch playlist:', err);
    error.value = err.message || "Could not connect to the server.";
  }
}

// --- Playback Methods ---
const playSong = async () => {
  try {
    await audioRef.value.play();
    isPlaying.value = true;
  } catch (err) {
    console.warn('❌ Autoplay was prevented:', err.message);
    isPlaying.value = false;
  }
};

const pauseSong = () => {
  audioRef.value.pause();
  isPlaying.value = false;
};

const togglePlay = () => {
  if (isPlaying.value) {
    pauseSong();
  } else {
    playSong();
  }
};

const resetAndPlay = () => {
  nextTick(() => {
    if (isPlaying.value) {
      playSong();
    }
  });
};

const nextTrack = () => {
  if (isShuffle.value) {
    let next = Math.floor(Math.random() * playlist.value.length);
    while (next === activeIndex.value && playlist.value.length > 1) {
      next = Math.floor(Math.random() * playlist.value.length);
    }
    activeIndex.value = next;
  } else {
    activeIndex.value = (activeIndex.value + 1) % playlist.value.length;
  }
  resetAndPlay();
};

const prevTrack = () => {
  activeIndex.value = (activeIndex.value - 1 + playlist.value.length) % playlist.value.length;
  resetAndPlay();
};

const handleTrackEnd = () => {
  if (isRepeating.value) {
    audioRef.value.currentTime = 0;
    playSong();
  } else {
    nextTrack();
  }
};

// --- Event Handlers ---
const updateTime = () => {
  if (audioRef.value) {
    currentTime.value = audioRef.value.currentTime;
  }
};

const setDuration = () => {
  if (audioRef.value) {
    duration.value = audioRef.value.duration || 0;
  }
};

const seekAudio = (e) => {
  if (!duration.value) return;
  const progressContainer = e.currentTarget;
  const clickX = e.offsetX;
  const width = progressContainer.clientWidth;
  audioRef.value.currentTime = (clickX / width) * duration.value;
};

const changeVolume = () => {
  if (audioRef.value) {
    audioRef.value.volume = volume.value;
    localStorage.setItem('music-volume', String(volume.value));
  }
};

const toggleShuffle = () => { isShuffle.value = !isShuffle.value; };
const toggleRepeat = () => { isRepeating.value = !isRepeating.value; };

const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value;
};

// --- Draggable Methods ---
const startDragging = (e) => {
  const tagName = e.target.tagName;
  const preventDragTags = ['BUTTON', 'INPUT', 'SVG', 'PATH', 'RECT', 'POLYGON', 'LINE', 'H3', 'P', 'SPAN'];
  if (preventDragTags.includes(tagName) || e.target.classList.contains('progress-container')) {
    return;
  }

  isDragging.value = true;
  initialX.value = e.clientX;
  initialY.value = e.clientY;
  offsetX.value = x.value - initialX.value;
  offsetY.value = y.value - initialY.value;
};

const drag = (e) => {
  if (isDragging.value) {
    const newX = e.clientX + offsetX.value;
    const newY = e.clientY + offsetY.value;
    
    const horizontalPadding = isCollapsed.value ? 2 * 16 : 2 * 24;
    const playerWidth = (isCollapsed.value ? 350 : 300) + horizontalPadding;

    const verticalPadding = isCollapsed.value ? 2 * 8 : 2 * 24;
    const playerHeight = (isCollapsed.value ? 80 : 400) + verticalPadding;
    
    x.value = Math.max(0, Math.min(window.innerWidth - playerWidth, newX));
    y.value = Math.max(0, Math.min(window.innerHeight - playerHeight, newY));

    // Persist position to local storage
    localStorage.setItem('player-x', x.value);
    localStorage.setItem('player-y', y.value);
    
    e.preventDefault();
  }
};

const stopDragging = () => {
  isDragging.value = false;
};

// --- Utility & Lifecycle ---
function formatTime(seconds) {
  if (!seconds || isNaN(seconds)) return '0:00';
  const minutes = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${minutes}:${String(secs).padStart(2, '0')}`;
}

onMounted(async () => {
  await fetchPlaylist();
  if (audioRef.value) {
    audioRef.value.volume = volume.value;
  }
  document.addEventListener('mousemove', drag);
  document.addEventListener('mouseup', stopDragging);
});

onUnmounted(() => {
  document.removeEventListener('mousemove', drag);
  document.removeEventListener('mouseup', stopDragging);
});
</script>

<style scoped>
/* Main container for the fixed-position collapsed player */
.music-player-container {
  position: fixed;
  top: 0;
  left: 0;
  z-index: 1000;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  /* The transition helps when it snaps back into place on expand/collapse */
  transition: transform 0.1s linear; 
}

/* Expanded Player UI */
.music-player-card {
  position: relative;
  background-color: #ffffff;
  border-radius: 16px;
  padding: 1.5rem; /* This is 24px */
  text-align: center;
  color: #333;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
  width: 300px;
}
.close-btn-container {
  position: absolute;
  top: 10px;
  right: 10px;
}
.close-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 10px;
  color: #6c757d;
  transition: transform 0.2s ease;
}
.close-btn:hover {
  transform: scale(1.1);
  color: #495057;
}
.close-btn .up-arrow {
  transform: rotate(180deg);
  transition: transform 0.3s ease;
  width: 28px;
  height: 28px;
}

/* Collapsed Player UI */
.music-player-collapsed {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 350px;
  height: 80px;
  background-color: #ffffff;
  border-radius: 12px;
  padding: 0.5rem 1rem; /* 1rem is 16px, 0.5rem is 8px */
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
  cursor: pointer;
  transition: all 0.3s ease;
}
.music-player-collapsed:hover {
  box-shadow: 0 6px 15px rgba(0,0,0,0.15);
}

.song-info-collapsed {
  display: flex;
  align-items: center;
  gap: 15px;
  flex-grow: 1;
}

.collapsed-album-art {
  width: 50px;
  height: 50px;
  border-radius: 8px;
  object-fit: cover;
}

.text-info {
  display: flex;
  flex-direction: column;
  text-align: left;
}
.text-info .song-title {
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 150px;
}
.text-info .song-artist {
  font-size: 0.9rem;
  color: #6c757d;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 150px;
}
.controls-collapsed {
  display: flex;
  align-items: center;
  gap: 1rem;
}

/* Existing styles for the expanded player */
.album-art-container {
  margin-bottom: 1.5rem;
}

.album-art {
  width: 150px;
  height: 150px;
  border-radius: 12px;
  object-fit: cover;
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}

.album-art.playing {
  animation: pulse 2s infinite ease-in-out;
}

@keyframes pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.03); }
  100% { transform: scale(1); }
}

.song-info {
  margin-bottom: 1rem;
}

.song-title {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0 0 0.25rem;
}

.song-artist {
  font-size: 0.9rem;
  color: #6c757d;
  margin: 0;
}

.progress-container {
  background-color: #e9ecef;
  border-radius: 5px;
  height: 6px;
  cursor: pointer;
  margin-bottom: 0.5rem;
}

.progress-bar {
  background-color: #4a148c;
  border-radius: 5px;
  height: 100%;
  width: 0%;
  transition: width 0.1s linear;
}

.time-display {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  color: #6c757d;
  margin-bottom: 1rem;
}

.controls {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1.5rem;
  margin-bottom: 1rem;
}

.control-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: #4a148c;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s ease, color 0.2s ease;
}
.control-btn:hover {
  transform: scale(1.1);
}
.control-btn.active {
    color: #8a2be2;
}

.play-pause-btn {
  background-color: #f3e8fd;
  border-radius: 50%;
  width: 50px;
  height: 50px;
}
.play-pause-btn:hover {
    background-color: #e9d5ff;
}

.secondary-controls {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
}

.small-btn {
    color: #999;
}
.small-btn:hover {
    color: #4a148c;
}
.small-btn.active {
    color: #8a2be2;
}

.volume-control {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    flex-grow: 1;
    margin: 0 1rem;
    color: #6c757d;
}

input[type='range'] {
  flex-grow: 1;
  accent-color: #8a2be2;
  height: 4px;
}
.error-state {
    padding: 2rem;
    color: #721c24;
    background-color: #f8d7da;
    border-radius: 8px;
}
.error-message {
    font-size: 0.9rem;
    color: #842029;
}
</style>