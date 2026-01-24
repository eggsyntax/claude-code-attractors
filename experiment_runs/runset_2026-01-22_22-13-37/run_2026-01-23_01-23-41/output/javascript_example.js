// Example JavaScript file to demonstrate multi-language analysis
const fs = require('fs');
const path = require('path');

class DataManager {
    constructor(config) {
        this.config = config;
        this.cache = new Map();
    }

    // Simple method
    getId() {
        return this.config.id;
    }

    // Complex method with high cyclomatic complexity
    processData(items, options = {}) {
        const results = [];
        const { threshold = 0.5, enableCaching = true, strict = false } = options;

        if (!Array.isArray(items)) {
            throw new Error('Items must be an array');
        }

        for (const item of items) {
            if (item.status === 'active') {
                if (item.priority === 'high') {
                    if (item.score > threshold) {
                        if (enableCaching && !this.cache.has(item.id)) {
                            const processed = this.processHighPriority(item);
                            if (processed) {
                                if (this.validateItem(processed)) {
                                    results.push(processed);
                                    this.cache.set(item.id, processed);
                                } else if (!strict) {
                                    results.push(processed);
                                }
                            }
                        } else if (this.cache.has(item.id)) {
                            results.push(this.cache.get(item.id));
                        }
                    }
                } else if (item.priority === 'medium') {
                    if (item.score > threshold * 0.8) {
                        results.push(this.processStandardItem(item));
                    }
                }
            } else if (item.status === 'pending') {
                if ((item.retryCount || 0) < 3) {
                    item.retryCount = (item.retryCount || 0) + 1;
                    results.push(item);
                }
            }
        }

        return strict ? results.filter(item => item.validated) : results;
    }

    processHighPriority(item) {
        return {
            ...item,
            processedAt: Date.now(),
            priorityBoost: 1.5
        };
    }

    processStandardItem(item) {
        return {
            ...item,
            processedAt: Date.now(),
            standard: true
        };
    }

    validateItem(item) {
        return item && item.id && item.status && item.priority;
    }

    // Async method
    async loadData(filename) {
        try {
            const data = await fs.promises.readFile(filename, 'utf8');
            return JSON.parse(data);
        } catch (error) {
            console.error(`Failed to load data: ${error.message}`);
            return null;
        }
    }
}

// Arrow functions
const helper = (data) => data.map(item => ({ ...item, processed: true }));

const complexHelper = (items, config) => {
    return items.reduce((acc, item) => {
        if (config.includeActive && item.status === 'active') {
            acc.active.push(item);
        } else if (config.includePending && item.status === 'pending') {
            acc.pending.push(item);
        }
        return acc;
    }, { active: [], pending: [] });
};

// Export for module system
module.exports = { DataManager, helper, complexHelper };