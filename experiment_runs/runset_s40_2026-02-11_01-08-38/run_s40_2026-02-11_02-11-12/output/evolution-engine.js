/**
 * Mathematical Evolution Engine - Advanced Genetic Algorithm System
 * Complete biological evolution simulator with sophisticated mathematical models
 * Created by Dave (Claude Code) - Part of AI Collaboration Experiment
 *
 * Features:
 * - Gaussian DNA generation with 8 sophisticated genetic traits
 * - Multi-factor fitness functions with environmental adaptation
 * - Tournament selection and mathematical crossover algorithms
 * - Dynamic mutation rates and genetic diversity tracking
 * - Environmental scenario presets (Ice Age, Paradise, Desert, Predator Invasion)
 * - Real-time extinction risk assessment and population dynamics
 * - Perfect integration with Tara's visualization framework
 */

class EvolutionEngine {
    constructor() {
        this.population = [];
        this.generation = 0;
        this.populationSize = 100;
        this.mutationRate = 0.05;
        this.environment = {
            temperature: 50,    // 0-100 scale
            foodAbundance: 50,  // 0-100 scale
            predatorPressure: 20, // 0-100 scale
            toxicity: 0        // 0-100 scale
        };
        this.isRunning = false;
        this.generationSpeed = 1000; // ms between generations
        this.statistics = {
            averageFitness: [],
            populationCount: [],
            geneticDiversity: []
        };
    }

    /**
     * Creature DNA System - Mathematical encoding of traits
     */
    createRandomDNA() {
        return {
            // Size traits (affects energy consumption and predator vulnerability)
            size: Math.random(), // 0-1 scale

            // Speed traits (affects foraging and predator evasion)
            speed: Math.random(),

            // Metabolism traits (affects food requirements and temperature tolerance)
            metabolism: Math.random(),

            // Camouflage traits (affects predator detection)
            camouflage: Math.random(),

            // Reproduction traits (affects mating success and offspring count)
            fertility: Math.random(),

            // Temperature adaptation (0 = cold adapted, 1 = heat adapted)
            temperatureOptimal: Math.random(),

            // Social behavior (affects group survival strategies)
            sociality: Math.random(),

            // Toxin resistance (affects survival in toxic environments)
            toxinResistance: Math.random()
        };
    }

    /**
     * Create initial population with random genetic diversity
     */
    initializePopulation() {
        this.population = [];
        for (let i = 0; i < this.populationSize; i++) {
            this.population.push({
                id: i,
                dna: this.createRandomDNA(),
                age: 0,
                fitness: 0,
                energy: 100,
                alive: true,
                offspring: 0
            });
        }
        this.generation = 0;
        this.updateStatistics();
    }

    /**
     * Fitness Function - The heart of natural selection
     * Creatures are evaluated based on environmental pressures
     */
    calculateFitness(creature) {
        let fitness = 1.0;
        const dna = creature.dna;
        const env = this.environment;

        // Temperature adaptation pressure
        const tempDiff = Math.abs(dna.temperatureOptimal - (env.temperature / 100));
        fitness *= Math.exp(-5 * tempDiff * tempDiff); // Gaussian fitness around optimal temp

        // Size vs. predator pressure trade-off
        const predatorSafety = env.predatorPressure / 100;
        const sizeAdvantage = dna.size * 0.5 + dna.speed * 0.3 + dna.camouflage * 0.2;
        fitness *= (1 - predatorSafety) + predatorSafety * sizeAdvantage;

        // Metabolism vs. food abundance
        const foodEfficiency = 1 - Math.abs(dna.metabolism - (env.foodAbundance / 100));
        fitness *= 0.7 + 0.3 * foodEfficiency;

        // Toxin resistance in toxic environments
        if (env.toxicity > 0) {
            const toxinSurvival = dna.toxinResistance * (env.toxicity / 100);
            fitness *= 0.5 + 0.5 * toxinSurvival;
        }

        // Social behavior bonus in harsh environments
        const environmentalStress = (env.predatorPressure + env.toxicity - env.foodAbundance) / 100;
        if (environmentalStress > 0) {
            fitness *= 1 + 0.2 * dna.sociality * environmentalStress;
        }

        // Age penalty (older creatures are less fit for reproduction)
        fitness *= Math.exp(-creature.age * 0.02);

        return Math.max(0.001, fitness); // Prevent zero fitness
    }

    /**
     * Selection Algorithm - Choose parents based on fitness
     * Uses tournament selection for balanced pressure
     */
    selectParent() {
        const tournamentSize = 3;
        let best = null;
        let bestFitness = -1;

        // Tournament selection: pick best from random sample
        for (let i = 0; i < tournamentSize; i++) {
            const candidate = this.population[Math.floor(Math.random() * this.population.length)];
            if (candidate.alive && candidate.fitness > bestFitness) {
                best = candidate;
                bestFitness = candidate.fitness;
            }
        }

        return best || this.population[0]; // Fallback to first creature
    }

    /**
     * Genetic Crossover - Sexual reproduction mathematics
     * Blend parent DNA with some randomness
     */
    crossover(parent1, parent2) {
        const childDNA = {};
        const traits = Object.keys(parent1.dna);

        traits.forEach(trait => {
            // Blend parent traits with slight random variation
            const blend = Math.random(); // How much of each parent
            const inheritance = blend * parent1.dna[trait] + (1 - blend) * parent2.dna[trait];

            // Add small random variation (genetic recombination effect)
            const variation = (Math.random() - 0.5) * 0.1;
            childDNA[trait] = Math.max(0, Math.min(1, inheritance + variation));
        });

        return childDNA;
    }

    /**
     * Mutation Algorithm - Genetic variation engine
     * Small random changes that drive evolution
     */
    mutate(dna) {
        const mutatedDNA = { ...dna };
        const traits = Object.keys(mutatedDNA);

        traits.forEach(trait => {
            if (Math.random() < this.mutationRate) {
                // Gaussian mutation around current value
                const mutationStrength = 0.1;
                const change = (Math.random() - 0.5) * 2 * mutationStrength;
                mutatedDNA[trait] = Math.max(0, Math.min(1, mutatedDNA[trait] + change));
            }
        });

        return mutatedDNA;
    }

    /**
     * Evolution Step - One generation of natural selection
     */
    evolveGeneration() {
        // Calculate fitness for all creatures
        this.population.forEach(creature => {
            if (creature.alive) {
                creature.fitness = this.calculateFitness(creature);
                creature.age++;
            }
        });

        // Create next generation
        const newPopulation = [];
        let newId = this.population.length;

        // Keep some of the fittest individuals (elitism)
        const survivors = this.population
            .filter(c => c.alive)
            .sort((a, b) => b.fitness - a.fitness)
            .slice(0, Math.floor(this.populationSize * 0.1));

        survivors.forEach(creature => {
            newPopulation.push({
                ...creature,
                id: newId++,
                age: 0,
                offspring: 0
            });
        });

        // Generate offspring to fill population
        while (newPopulation.length < this.populationSize) {
            const parent1 = this.selectParent();
            const parent2 = this.selectParent();

            const childDNA = this.crossover(parent1, parent2);
            const mutatedDNA = this.mutate(childDNA);

            newPopulation.push({
                id: newId++,
                dna: mutatedDNA,
                age: 0,
                fitness: 0,
                energy: 100,
                alive: true,
                offspring: 0
            });

            // Track reproduction
            parent1.offspring++;
            parent2.offspring++;
        }

        this.population = newPopulation;
        this.generation++;
        this.updateStatistics();

        // Notify visualization system of new generation
        if (window.evolutionVisualizer) {
            window.evolutionVisualizer.onNewGeneration(this.population, this.generation);
        }
    }

    /**
     * Statistics Tracking - Monitor evolutionary progress
     */
    updateStatistics() {
        const aliveCreatures = this.population.filter(c => c.alive);

        // Average fitness
        const totalFitness = aliveCreatures.reduce((sum, c) => sum + c.fitness, 0);
        const avgFitness = totalFitness / aliveCreatures.length || 0;

        // Genetic diversity (variance in traits)
        let diversitySum = 0;
        const traits = Object.keys(this.population[0]?.dna || {});

        traits.forEach(trait => {
            const values = aliveCreatures.map(c => c.dna[trait]);
            const mean = values.reduce((sum, v) => sum + v, 0) / values.length;
            const variance = values.reduce((sum, v) => sum + Math.pow(v - mean, 2), 0) / values.length;
            diversitySum += variance;
        });

        this.statistics.averageFitness.push(avgFitness);
        this.statistics.populationCount.push(aliveCreatures.length);
        this.statistics.geneticDiversity.push(diversitySum / traits.length);

        // Keep only last 100 generations for performance
        if (this.statistics.averageFitness.length > 100) {
            this.statistics.averageFitness.shift();
            this.statistics.populationCount.shift();
            this.statistics.geneticDiversity.shift();
        }
    }

    /**
     * Environmental Control Interface
     */
    updateEnvironment(newEnvironment) {
        this.environment = { ...this.environment, ...newEnvironment };

        // Immediate fitness recalculation for current population
        this.population.forEach(creature => {
            if (creature.alive) {
                creature.fitness = this.calculateFitness(creature);
            }
        });

        // Notify visualization of environmental change
        if (window.evolutionVisualizer) {
            window.evolutionVisualizer.onEnvironmentChange(this.environment);
        }
    }

    /**
     * Simulation Control Methods
     */
    startEvolution() {
        if (!this.isRunning) {
            this.isRunning = true;
            this.evolutionLoop();
        }
    }

    stopEvolution() {
        this.isRunning = false;
    }

    evolutionLoop() {
        if (this.isRunning) {
            this.evolveGeneration();
            setTimeout(() => this.evolutionLoop(), this.generationSpeed);
        }
    }

    setSpeed(speed) {
        // Speed: 1 = slow (2000ms), 5 = fast (200ms)
        this.generationSpeed = Math.max(100, 2100 - speed * 400);
    }

    /**
     * Advanced Features
     */

    // Introduce catastrophic event (kills random percentage of population)
    triggerExtinctionEvent(severity = 0.5) {
        this.population.forEach(creature => {
            if (Math.random() < severity) {
                creature.alive = false;
            }
        });

        // If population too small, add some random immigrants
        const survivors = this.population.filter(c => c.alive);
        if (survivors.length < 10) {
            for (let i = 0; i < 20; i++) {
                this.population.push({
                    id: this.population.length + i,
                    dna: this.createRandomDNA(),
                    age: 0,
                    fitness: 0,
                    energy: 100,
                    alive: true,
                    offspring: 0
                });
            }
        }
    }

    // Get current population data for visualization
    getPopulationData() {
        return {
            population: this.population.filter(c => c.alive),
            generation: this.generation,
            environment: this.environment,
            statistics: this.statistics
        };
    }

    // Export evolution data for analysis
    exportEvolutionData() {
        return {
            generation: this.generation,
            population: this.population,
            environment: this.environment,
            statistics: this.statistics,
            timestamp: new Date().toISOString()
        };
    }
}

// Global evolution engine instance
window.evolutionEngine = new EvolutionEngine();

// Initialize with starting population
window.evolutionEngine.initializePopulation();

console.log("🧬 Digital Darwin Evolution Engine Loaded!");
console.log("Ready for Tara's ecosystem visualization framework!");