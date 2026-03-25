/**
 * Fractal Music Laboratory - Mathematical Audio Engine
 * A collaboration between Dave and Tara - Claude Code instances
 *
 * This engine transforms mathematical concepts into musical compositions using:
 * - Fractal melody generation with recursive patterns
 * - Golden ratio rhythm calculations
 * - Fibonacci interval sequences
 * - Chaos theory for organic variation
 * - Real-time Web Audio API synthesis
 */

class FractalMusicEngine {
    constructor() {
        this.audioContext = null;
        this.isPlaying = false;
        this.oscillators = [];
        this.gainNodes = [];
        this.masterGain = null;
        this.currentParameters = null;
        this.melodyPattern = [];
        this.rhythmPattern = [];
        this.harmonyPattern = [];
        this.playbackTimer = null;
        this.noteIndex = 0;

        // Mathematical constants
        this.PHI = (1 + Math.sqrt(5)) / 2; // Golden ratio
        this.FIBONACCI = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89];
        this.CHROMATIC_SCALE = [261.63, 277.18, 293.66, 311.13, 329.63, 349.23, 369.99, 392.00, 415.30, 440.00, 466.16, 493.88]; // C4 to B4

        this.initializeAudioContext();
    }

    async initializeAudioContext() {
        try {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            this.masterGain = this.audioContext.createGain();
            this.masterGain.connect(this.audioContext.destination);
            this.masterGain.gain.setValueAtTime(0.3, this.audioContext.currentTime);

            console.log('🎵 Fractal Music Engine initialized successfully!');
        } catch (error) {
            console.error('❌ Audio context initialization failed:', error);
        }
    }

    /**
     * Generate fractal melody using recursive mathematical patterns
     */
    generateFractalMelody(depth, basePattern, goldenRatio) {
        if (depth <= 0) return basePattern;

        const newPattern = [];

        // Apply fractal recursion with golden ratio scaling
        for (let i = 0; i < basePattern.length; i++) {
            const note = basePattern[i];
            newPattern.push(note);

            // Generate smaller fractal patterns
            const subPattern = this.generateFractalMelody(
                depth - 1,
                [note * goldenRatio, note / goldenRatio],
                goldenRatio
            );

            newPattern.push(...subPattern);
        }

        // Apply mathematical transformation to keep notes in musical range
        return newPattern.map(note => {
            const scaledNote = Math.abs(note) % this.CHROMATIC_SCALE.length;
            return this.CHROMATIC_SCALE[Math.floor(scaledNote)];
        });
    }

    /**
     * Generate rhythm pattern using Fibonacci sequences
     */
    generateFibonacciRhythm(fibScale, tempo) {
        const rhythmPattern = [];
        const baseUnit = 60000 / tempo; // Convert BPM to milliseconds

        for (let i = 0; i < 8; i++) {
            const fibIndex = (i * fibScale) % this.FIBONACCI.length;
            const fibValue = this.FIBONACCI[fibIndex];
            const noteDuration = baseUnit * (fibValue / 8 + 0.25); // Normalize and add base duration
            rhythmPattern.push(noteDuration);
        }

        return rhythmPattern;
    }

    /**
     * Generate harmony using golden ratio intervals
     */
    generateGoldenHarmony(baseFreq, goldenRatio) {
        const harmonics = [];

        // Generate harmonic series based on golden ratio
        for (let i = 0; i < 4; i++) {
            const harmonic = baseFreq * Math.pow(goldenRatio, i / 2);
            harmonics.push(this.quantizeToScale(harmonic));
        }

        return harmonics;
    }

    /**
     * Quantize frequency to nearest chromatic scale note
     */
    quantizeToScale(frequency) {
        let closestNote = this.CHROMATIC_SCALE[0];
        let minDistance = Math.abs(frequency - closestNote);

        for (const note of this.CHROMATIC_SCALE) {
            const distance = Math.abs(frequency - note);
            if (distance < minDistance) {
                minDistance = distance;
                closestNote = note;
            }
        }

        return closestNote;
    }

    /**
     * Apply chaos theory variation to introduce organic unpredictability
     */
    applyChaosVariation(pattern, chaosFactor) {
        return pattern.map(value => {
            const chaosVariation = (Math.random() - 0.5) * chaosFactor;
            return value * (1 + chaosVariation);
        });
    }

    /**
     * Evaluate mathematical expressions for melody/rhythm/harmony
     */
    evaluateEquation(equation, x, n) {
        try {
            // Create safe evaluation context
            const context = {
                x: x,
                n: n,
                phi: this.PHI,
                fibonacci: (index) => this.FIBONACCI[Math.abs(Math.floor(index)) % this.FIBONACCI.length],
                sin: Math.sin,
                cos: Math.cos,
                tan: Math.tan,
                sqrt: Math.sqrt,
                pow: Math.pow,
                abs: Math.abs,
                floor: Math.floor,
                ceil: Math.ceil,
                random: Math.random,
                PI: Math.PI,
                E: Math.E
            };

            // Simple expression evaluator (in production, use a proper math parser)
            let result = equation;
            Object.keys(context).forEach(key => {
                const regex = new RegExp(`\\b${key}\\b`, 'g');
                result = result.replace(regex, context[key]);
            });

            // Evaluate basic mathematical operations
            try {
                return Function('"use strict"; return (' + result + ')')();
            } catch {
                return Math.sin(x) + n; // Fallback pattern
            }
        } catch (error) {
            console.warn('Equation evaluation error:', error);
            return Math.sin(x) + n; // Fallback to simple pattern
        }
    }

    /**
     * Generate complete musical composition from parameters
     */
    generateComposition(parameters) {
        const {
            fractalDepth,
            goldenRatio,
            fibonacciScale,
            chaosFactor,
            tempo,
            melodyEquation,
            rhythmEquation,
            harmonyEquation
        } = parameters;

        // Generate base patterns from equations
        const melodyBase = [];
        const rhythmBase = [];
        const harmonyBase = [];

        for (let i = 0; i < 16; i++) {
            melodyBase.push(this.evaluateEquation(melodyEquation, i * 0.5, i));
            rhythmBase.push(this.evaluateEquation(rhythmEquation, i * 0.25, i));
            harmonyBase.push(this.evaluateEquation(harmonyEquation, i * 0.75, i));
        }

        // Apply mathematical transformations
        this.melodyPattern = this.generateFractalMelody(fractalDepth, melodyBase, goldenRatio);
        this.rhythmPattern = this.generateFibonacciRhythm(fibonacciScale, tempo);
        this.harmonyPattern = this.applyChaosVariation(harmonyBase, chaosFactor);

        // Normalize patterns to reasonable musical ranges
        this.melodyPattern = this.melodyPattern.map(freq => this.quantizeToScale(Math.abs(freq) + 200));
        this.harmonyPattern = this.harmonyPattern.map(freq => this.quantizeToScale(Math.abs(freq) + 300));

        console.log('🎼 Mathematical composition generated:', {
            melodyLength: this.melodyPattern.length,
            rhythmLength: this.rhythmPattern.length,
            harmonyLength: this.harmonyPattern.length
        });
    }

    /**
     * Create and play a single note with harmonics
     */
    playNote(frequency, duration, harmonics = []) {
        if (!this.audioContext) return;

        const now = this.audioContext.currentTime;

        // Main oscillator
        const oscillator = this.audioContext.createOscillator();
        const gainNode = this.audioContext.createGain();

        oscillator.connect(gainNode);
        gainNode.connect(this.masterGain);

        oscillator.frequency.setValueAtTime(frequency, now);
        oscillator.type = 'sine';

        // ADSR envelope
        gainNode.gain.setValueAtTime(0, now);
        gainNode.gain.linearRampToValueAtTime(0.3, now + duration * 0.1);
        gainNode.gain.exponentialRampToValueAtTime(0.2, now + duration * 0.3);
        gainNode.gain.setValueAtTime(0.2, now + duration * 0.7);
        gainNode.gain.exponentialRampToValueAtTime(0.01, now + duration);

        oscillator.start(now);
        oscillator.stop(now + duration);

        // Add harmonics
        harmonics.forEach((harmonic, index) => {
            if (index < 3) { // Limit harmonics to avoid audio clutter
                const harmOsc = this.audioContext.createOscillator();
                const harmGain = this.audioContext.createGain();

                harmOsc.connect(harmGain);
                harmGain.connect(this.masterGain);

                harmOsc.frequency.setValueAtTime(harmonic, now);
                harmOsc.type = 'triangle';

                const harmonicVolume = 0.1 / (index + 1);
                harmGain.gain.setValueAtTime(harmonicVolume, now);
                harmGain.gain.exponentialRampToValueAtTime(0.01, now + duration);

                harmOsc.start(now);
                harmOsc.stop(now + duration);

                this.oscillators.push(harmOsc);
                this.gainNodes.push(harmGain);
            }
        });

        this.oscillators.push(oscillator);
        this.gainNodes.push(gainNode);

        // Clean up finished oscillators
        setTimeout(() => {
            const oscIndex = this.oscillators.indexOf(oscillator);
            if (oscIndex > -1) {
                this.oscillators.splice(oscIndex, 1);
                this.gainNodes.splice(oscIndex, 1);
            }
        }, duration * 1000);
    }

    /**
     * Start musical playback with mathematical patterns
     */
    startPlayback(parameters) {
        if (this.isPlaying) return;

        this.currentParameters = parameters;
        this.isPlaying = true;
        this.noteIndex = 0;

        // Generate composition from mathematical parameters
        this.generateComposition(parameters);

        console.log('🎵 Starting fractal music playback...');

        // Start playback loop
        this.scheduleNextNote();
    }

    /**
     * Schedule and play the next note in the pattern
     */
    scheduleNextNote() {
        if (!this.isPlaying || !this.melodyPattern.length) return;

        const melodyNote = this.melodyPattern[this.noteIndex % this.melodyPattern.length];
        const rhythmDuration = this.rhythmPattern[this.noteIndex % this.rhythmPattern.length];
        const harmonics = this.generateGoldenHarmony(melodyNote, this.currentParameters.goldenRatio);

        // Play the note with harmonics
        this.playNote(melodyNote, rhythmDuration / 1000, harmonics);

        // Update visualization (call back to Tara's visual system)
        if (window.updateVisualizationWithAudio) {
            window.updateVisualizationWithAudio({
                frequency: melodyNote,
                harmonics: harmonics,
                noteIndex: this.noteIndex,
                rhythmDuration: rhythmDuration
            });
        }

        // Schedule next note
        this.playbackTimer = setTimeout(() => {
            this.noteIndex++;
            this.scheduleNextNote();
        }, rhythmDuration);
    }

    /**
     * Stop musical playback
     */
    stopPlayback() {
        this.isPlaying = false;

        if (this.playbackTimer) {
            clearTimeout(this.playbackTimer);
            this.playbackTimer = null;
        }

        // Stop all currently playing oscillators
        this.oscillators.forEach(osc => {
            try {
                osc.stop();
            } catch (e) {
                // Oscillator may have already stopped
            }
        });

        this.oscillators = [];
        this.gainNodes = [];
        this.noteIndex = 0;

        console.log('🛑 Fractal music playback stopped');
    }

    /**
     * Get current audio analysis data for visualization
     */
    getAudioAnalysis() {
        if (!this.audioContext) return null;

        const analyser = this.audioContext.createAnalyser();
        this.masterGain.connect(analyser);

        analyser.fftSize = 256;
        const bufferLength = analyser.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);
        analyser.getByteFrequencyData(dataArray);

        return {
            frequencyData: dataArray,
            currentNote: this.melodyPattern[this.noteIndex % this.melodyPattern.length],
            patternProgress: this.noteIndex / this.melodyPattern.length
        };
    }
}

// Initialize and expose the fractal music engine
window.fractalMusicEngine = new FractalMusicEngine();

// Preset mathematical equations for instant inspiration
window.fractalMusicPresets = {
    "Golden Spiral": {
        melody: "sin(x * phi) + fibonacci(n % 8)",
        rhythm: "cos(x / phi) + fibonacci((n + 2) % 8)",
        harmony: "sin(x) * phi + cos(n * phi)"
    },
    "Fibonacci Dreams": {
        melody: "fibonacci(n % 12) + sin(x * 2)",
        rhythm: "fibonacci((n + 1) % 8) + cos(x)",
        harmony: "fibonacci(n % 6) * cos(x * phi)"
    },
    "Chaos Symphony": {
        melody: "sin(x * chaos) + fibonacci(floor(random() * 8))",
        rhythm: "cos(x + random() * chaos) + fibonacci(n % 6)",
        harmony: "sin(x * phi) + cos(n * chaos) * fibonacci(n % 4)"
    },
    "Mathematical Harmony": {
        melody: "sin(x * PI) + cos(x * phi) + fibonacci(n % 8)",
        rhythm: "fibonacci(n % 8) + sin(x * 2) + cos(x / phi)",
        harmony: "sin(x) * cos(n * phi) + fibonacci((n * 2) % 8)"
    }
};

console.log('🎼✨ Fractal Music Laboratory - Mathematical Audio Engine Ready!');
console.log('🔢🎵 Ready to transform mathematics into music!');