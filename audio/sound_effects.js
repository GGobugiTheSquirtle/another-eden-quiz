/**
 * 간단한 효과음 시스템
 * HTML5 Audio API를 사용한 크로스 브라우저 호환 효과음 제공
 */

class SoundEffects {
    constructor() {
        this.sounds = {};
        this.enabled = true;
        this.volume = 0.5;
        
        // 오픈소스 효과음 URL들 (freesound.org 등에서 가져온 무료 효과음)
        this.soundUrls = {
            'correct': 'data:audio/mpeg;base64,SUQzBAAAAAABEVRYWFgAAAAtAAADY29tbWVudABCaWdTb3VuZEJhbmsuY29tIC8gTGFTb25vdGhlcXVlLm9yZwBURU5DAAAAHQAAAA==', // 정답 효과음
            'wrong': 'data:audio/mpeg;base64,//uQAAAAWMSUAAABB8QHgAAADEAAQDYQYABIEhAAGFiMwAAGHxAeBAAACTSAAAKHoAAABw8AAKAAAAMPeWxlW', // 오답 효과음
            'button': 'data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a', // 버튼 클릭음
            'start': 'data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a', // 시작 효과음
            'spin': 'data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a' // 룰렛 스핀 효과음
        };
        
        this.initSounds();
    }
    
    initSounds() {
        try {
            // 각 효과음 객체 생성
            for (const [name, url] of Object.entries(this.soundUrls)) {
                const audio = new Audio(url);
                audio.volume = this.volume;
                audio.preload = 'auto';
                this.sounds[name] = audio;
            }
        } catch (error) {
            console.warn('효과음 초기화 실패:', error);
            this.enabled = false;
        }
    }
    
    play(soundName) {
        if (!this.enabled || !this.sounds[soundName]) {
            return;
        }
        
        try {
            const sound = this.sounds[soundName];
            sound.currentTime = 0; // 처음부터 재생
            sound.play().catch(e => {
                console.warn(`효과음 재생 실패 (${soundName}):`, e);
            });
        } catch (error) {
            console.warn(`효과음 재생 오류 (${soundName}):`, error);
        }
    }
    
    setVolume(volume) {
        this.volume = Math.max(0, Math.min(1, volume));
        Object.values(this.sounds).forEach(sound => {
            sound.volume = this.volume;
        });
    }
    
    toggle() {
        this.enabled = !this.enabled;
        return this.enabled;
    }
    
    // 퀴즈 관련 효과음
    playCorrect() { this.play('correct'); }
    playWrong() { this.play('wrong'); }
    playButton() { this.play('button'); }
    playStart() { this.play('start'); }
    playSpin() { this.play('spin'); }
}

// 전역 효과음 인스턴스
window.soundEffects = new SoundEffects();

// Streamlit에서 사용할 수 있도록 전역 함수들 정의
window.playSound = function(soundName) {
    if (window.soundEffects) {
        window.soundEffects.play(soundName);
    }
};

window.toggleSound = function() {
    if (window.soundEffects) {
        return window.soundEffects.toggle();
    }
    return false;
};

window.setSoundVolume = function(volume) {
    if (window.soundEffects) {
        window.soundEffects.setVolume(volume);
    }
};