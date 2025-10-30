import {ref, computed, watch} from 'vue'
import {defineStore} from 'pinia'
import type {Song} from '@/types'
import {useAuthStore} from './auth'

type PlayMode = 'sequential' | 'repeat' | 'shuffle'

export const usePlayerStore = defineStore('player', () => {
    // 状态
    const currentSong = ref<Song | null>(null)
    const isPlaying = ref(false)
    const currentTime = ref(0)
    const duration = ref(0)
    const volume = ref(80)
    const isMuted = ref(false)
    const loading = ref(false)
    const playMode = ref<PlayMode>('sequential')
    const playlist = ref<Song[]>([])
    const currentIndex = ref(-1)

    // 音频元素
    let audio: HTMLAudioElement | null = null

    // 初始化音频
    const initAudio = () => {
        if (!audio) {
            audio = new Audio()
            audio.addEventListener('loadstart', () => loading.value = true)
            audio.addEventListener('loadeddata', () => {
                loading.value = false
                duration.value = audio?.duration || 0
            })
            audio.addEventListener('timeupdate', () => {
                if (audio && !audio.seeking) {
                    currentTime.value = audio.currentTime
                }
            })
            audio.addEventListener('ended', () => nextSong())
            audio.addEventListener('error', (e) => {
                console.error('Audio playback error', e)
                loading.value = false
                isPlaying.value = false
            })
            audio.addEventListener('canplay', () => loading.value = false)
        }
    }

    const hasPrevious = computed(() => playlist.value.length > 1);
    const hasNext = computed(() => playlist.value.length > 1);

    const progress = computed(() => {
        if (duration.value === 0) return 0
        return (currentTime.value / duration.value) * 100
    })

    const play = (song: Song) => {
        if (!song) return;

        if (currentSong.value?.id === song.id && audio?.src) {
            togglePlay()
            return
        }

        initAudio()
        if (!audio) return

        currentSong.value = song
        loading.value = true
        isPlaying.value = false;

        const authStore = useAuthStore()
        audio.src = authStore.token
            ? `http://localhost:8000/songs/${song.id}/stream?token=${encodeURIComponent(authStore.token)}`
            : `http://localhost:8000/songs/${song.id}/stream`

        audio.volume = volume.value / 100
        audio.muted = isMuted.value

        audio.play().then(() => {
            isPlaying.value = true
            loading.value = false
        }).catch((error) => {
            console.error('Failed to play audio:', error)
            isPlaying.value = false
            loading.value = false
        })
    }

    const playWithPlaylist = (song: Song, songs: Song[]) => {
        playlist.value = [...songs];

        const songIndex = playlist.value.findIndex(s => s.id === song.id)
        if (songIndex !== -1) {
            currentIndex.value = songIndex
            play(song)
        }
    }

    const togglePlay = () => {
        if (!audio || !currentSong.value) return

        if (isPlaying.value) {
            audio.pause()
            isPlaying.value = false
        } else {
            audio.play().catch((error) => console.error('Failed to resume audio:', error))
            isPlaying.value = true
        }
    }

    const stop = () => {
        if (!audio) return
        audio.pause()
        // === 彻底清空 src 以释放文件句柄 ===
        audio.src = ''
        audio.removeAttribute('src')
        audio.currentTime = 0
        isPlaying.value = false
        currentSong.value = null
        currentIndex.value = -1;
    }

    const seek = (percentage: number) => {
        if (!audio || !duration.value) return
        audio.currentTime = (percentage / 100) * duration.value
    }

    const setVolume = (newVolume: number) => {
        volume.value = Math.max(0, Math.min(100, newVolume))
        if (audio) audio.volume = volume.value / 100
        if (volume.value > 0 && isMuted.value) toggleMute()
    }

    const toggleMute = () => {
        isMuted.value = !isMuted.value
        if (audio) audio.muted = isMuted.value
    }

    const previousSong = () => {
        if (!hasPrevious.value) return;

        if (playMode.value === 'shuffle') {
            playRandomSong();
        } else {
            const prevIndex = (currentIndex.value - 1 + playlist.value.length) % playlist.value.length;
            playByIndex(prevIndex);
        }
    }

    const nextSong = () => {
        if (!hasNext.value && playMode.value !== 'repeat') return;

        if (playMode.value === 'repeat' && currentSong.value) {
            seek(0);
            play(currentSong.value);
            return;
        }

        if (playMode.value === 'shuffle') {
            playRandomSong();
        } else { // 顺序播放
            const nextIndex = (currentIndex.value + 1) % playlist.value.length;
            playByIndex(nextIndex);
        }
    }

    const playRandomSong = () => {
        if (playlist.value.length <= 1) return;
        let randomIndex;
        do {
            randomIndex = Math.floor(Math.random() * playlist.value.length);
        } while (randomIndex === currentIndex.value);
        playByIndex(randomIndex);
    }

    const playByIndex = (index: number) => {
        if (index >= 0 && index < playlist.value.length) {
            currentIndex.value = index
            play(playlist.value[index])
        }
    }

    const togglePlayMode = () => {
        const modes: PlayMode[] = ['sequential', 'repeat', 'shuffle']
        const currentModeIndex = modes.indexOf(playMode.value)
        playMode.value = modes[(currentModeIndex + 1) % modes.length]
    }

    const addToPlaylist = (song: Song) => {
        const exists = playlist.value.some(s => s.id === song.id)
        if (!exists) {
            playlist.value = [...playlist.value, song]
        }
    }

    const removeFromPlaylist = (songId: number) => {
        const indexToRemove = playlist.value.findIndex(s => s.id === songId);
        if (indexToRemove === -1) return;

        const wasPlayingRemovedSong = currentSong.value?.id === songId;

        playlist.value = playlist.value.filter(s => s.id !== songId);

        if (wasPlayingRemovedSong) {
            if (playlist.value.length > 0) {
                const nextIndex = indexToRemove % playlist.value.length;
                playByIndex(nextIndex);
            } else {
                stop();
            }
        } else if (indexToRemove < currentIndex.value) {
            currentIndex.value--;
        }
    }

    const clearPlaylist = () => {
        stop()
        playlist.value = []
    }

    watch(volume, (newVolume) => {
        if (audio) audio.volume = newVolume / 100
    })
    watch(isMuted, (muted) => {
        if (audio) audio.muted = muted
    })

    return {
        currentSong,
        isPlaying,
        currentTime,
        duration,
        volume,
        isMuted,
        loading,
        playMode,
        playlist,
        currentIndex,
        progress,
        hasPrevious,
        hasNext,
        initAudio,
        play,
        playWithPlaylist,
        togglePlay,
        stop,
        seek,
        setVolume,
        toggleMute,
        previousSong,
        nextSong,
        playByIndex,
        togglePlayMode,
        addToPlaylist,
        removeFromPlaylist,
        clearPlaylist
    }
})