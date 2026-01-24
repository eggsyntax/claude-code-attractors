#!/bin/bash
# Code Metrics Analyzer - Comprehensive Demo Script
# This script demonstrates the powerful capabilities of our Rust-based code analyzer

set -e  # Exit on any error

echo "🚀 CodeMetrics Analyzer - Comprehensive Demo"
echo "============================================="
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_step() {
    echo -e "${BLUE}🔹 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

# Check if we're in the right directory
if [[ ! -f "Cargo.toml" ]]; then
    echo -e "${RED}❌ Error: Please run this script from the project root directory${NC}"
    exit 1
fi

# Build the project
print_step "Building CodeMetrics Analyzer..."
if cargo build --release; then
    print_success "Build completed successfully!"
else
    echo -e "${RED}❌ Build failed. Please check for compilation errors.${NC}"
    exit 1
fi

echo

# Create test directories with sample code
print_step "Setting up demo workspace..."

mkdir -p demo_workspace/{rust_project,js_project,python_project,mixed_project}

# Create sample Rust project
cat > demo_workspace/rust_project/main.rs << 'EOF'
use std::collections::HashMap;

/// A complex function with high cyclomatic complexity
fn complex_business_logic(data: Vec<i32>, config: Config) -> Result<ProcessedData, Error> {
    let mut results = HashMap::new();
    let mut stats = Stats::default();

    for item in data.iter() {
        if *item > 0 {
            if *item < config.threshold {
                match item % 3 {
                    0 => {
                        if config.enable_special_processing {
                            for i in 0..*item {
                                if i % 2 == 0 {
                                    stats.even_count += 1;
                                    results.insert(i, format!("even_{}", i));
                                } else {
                                    stats.odd_count += 1;
                                    results.insert(i, format!("odd_{}", i));
                                }
                            }
                        }
                    },
                    1 => {
                        stats.mod_one_count += 1;
                        if *item > config.secondary_threshold {
                            results.insert(*item, format!("high_{}", item));
                        }
                    },
                    2 => {
                        stats.mod_two_count += 1;
                        results.insert(*item, format!("mod_two_{}", item));
                    },
                    _ => unreachable!()
                }
            } else {
                return Err(Error::ThresholdExceeded(*item));
            }
        } else if *item == 0 {
            stats.zero_count += 1;
        } else {
            stats.negative_count += 1;
            if config.allow_negative {
                results.insert(*item, format!("negative_{}", item.abs()));
            } else {
                return Err(Error::NegativeNotAllowed(*item));
            }
        }
    }

    if results.is_empty() {
        Err(Error::NoResults)
    } else {
        Ok(ProcessedData { results, stats })
    }
}

// Recursive function example
fn fibonacci(n: u32) -> u64 {
    match n {
        0 => 0,
        1 => 1,
        _ => fibonacci(n - 1) + fibonacci(n - 2),
    }
}

// Long function with many parameters (anti-pattern)
fn process_user_data(
    user_id: String,
    first_name: String,
    last_name: String,
    email: String,
    phone: Option<String>,
    address: Address,
    preferences: UserPreferences,
    subscription_type: SubscriptionType,
    created_at: chrono::DateTime<chrono::Utc>,
    updated_at: chrono::DateTime<chrono::Utc>,
    is_verified: bool,
    is_active: bool,
) -> ProcessedUser {
    // Function body with 50+ lines...
    let full_name = format!("{} {}", first_name, last_name);

    // Lots of processing logic here...
    let mut processed = ProcessedUser::new(user_id);
    processed.set_name(full_name);
    processed.set_email(email);

    if let Some(phone_num) = phone {
        processed.set_phone(phone_num);
    }

    processed.set_address(address);
    processed.set_preferences(preferences);
    processed.set_subscription(subscription_type);
    processed.set_timestamps(created_at, updated_at);
    processed.set_status(is_verified, is_active);

    processed
}

#[derive(Default)]
struct Stats {
    even_count: u32,
    odd_count: u32,
    mod_one_count: u32,
    mod_two_count: u32,
    zero_count: u32,
    negative_count: u32,
}

struct Config {
    threshold: i32,
    secondary_threshold: i32,
    enable_special_processing: bool,
    allow_negative: bool,
}

struct ProcessedData {
    results: HashMap<i32, String>,
    stats: Stats,
}

enum Error {
    ThresholdExceeded(i32),
    NegativeNotAllowed(i32),
    NoResults,
}

// Mock types
struct Address;
struct UserPreferences;
enum SubscriptionType { Free, Premium, Enterprise }
struct ProcessedUser { id: String }

impl ProcessedUser {
    fn new(id: String) -> Self { Self { id } }
    fn set_name(&mut self, _name: String) {}
    fn set_email(&mut self, _email: String) {}
    fn set_phone(&mut self, _phone: String) {}
    fn set_address(&mut self, _address: Address) {}
    fn set_preferences(&mut self, _prefs: UserPreferences) {}
    fn set_subscription(&mut self, _sub: SubscriptionType) {}
    fn set_timestamps(&mut self, _created: chrono::DateTime<chrono::Utc>, _updated: chrono::DateTime<chrono::Utc>) {}
    fn set_status(&mut self, _verified: bool, _active: bool) {}
}
EOF

# Create sample JavaScript project
cat > demo_workspace/js_project/app.js << 'EOF'
// JavaScript with various complexity patterns and security issues

// Security anti-pattern: eval usage
function dangerousEval(userInput) {
    return eval(`return ${userInput}`); // 🚨 Security risk
}

// XSS vulnerability
function updateDOM(userContent) {
    document.getElementById('content').innerHTML = userContent; // 🚨 XSS risk
}

// Complex async function with nested conditionals
async function fetchAndProcessData(urls, options = {}) {
    const { timeout = 5000, retries = 3, batchSize = 10 } = options;
    const results = [];

    for (let i = 0; i < urls.length; i += batchSize) {
        const batch = urls.slice(i, i + batchSize);
        const batchPromises = batch.map(async (url, index) => {
            let attempts = 0;

            while (attempts < retries) {
                try {
                    const controller = new AbortController();
                    const timeoutId = setTimeout(() => controller.abort(), timeout);

                    const response = await fetch(url, { signal: controller.signal });
                    clearTimeout(timeoutId);

                    if (!response.ok) {
                        if (response.status >= 500 && attempts < retries - 1) {
                            attempts++;
                            await new Promise(resolve => setTimeout(resolve, 1000 * attempts));
                            continue;
                        } else {
                            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                        }
                    }

                    const contentType = response.headers.get('content-type');
                    let data;

                    if (contentType && contentType.includes('application/json')) {
                        data = await response.json();

                        // Complex data validation
                        if (data && typeof data === 'object') {
                            if (data.status === 'success') {
                                if (data.results && Array.isArray(data.results)) {
                                    return { url, data: data.results, index };
                                } else {
                                    return { url, data: [], index };
                                }
                            } else if (data.status === 'error') {
                                throw new Error(data.message || 'Unknown error');
                            } else {
                                return { url, data: data, index };
                            }
                        } else {
                            throw new Error('Invalid response format');
                        }
                    } else if (contentType && contentType.includes('text/')) {
                        data = await response.text();
                        return { url, data: { text: data }, index };
                    } else {
                        data = await response.blob();
                        return { url, data: { blob: data }, index };
                    }

                } catch (error) {
                    if (error.name === 'AbortError') {
                        if (attempts < retries - 1) {
                            attempts++;
                            continue;
                        } else {
                            throw new Error(`Request timeout after ${retries} attempts`);
                        }
                    } else {
                        if (attempts < retries - 1) {
                            attempts++;
                            await new Promise(resolve => setTimeout(resolve, 1000 * attempts));
                            continue;
                        } else {
                            throw error;
                        }
                    }
                }
            }
        });

        try {
            const batchResults = await Promise.all(batchPromises);
            results.push(...batchResults);
        } catch (error) {
            console.error(`Batch ${Math.floor(i / batchSize)} failed:`, error);
            // Continue with next batch
        }
    }

    return results.sort((a, b) => a.index - b.index);
}

// Function with too many parameters
function createUser(
    firstName,
    lastName,
    email,
    phone,
    address,
    city,
    state,
    zipCode,
    country,
    birthDate,
    gender,
    preferences,
    notifications,
    subscription,
    referralCode
) {
    return {
        firstName,
        lastName,
        email,
        phone,
        address,
        city,
        state,
        zipCode,
        country,
        birthDate,
        gender,
        preferences,
        notifications,
        subscription,
        referralCode,
        createdAt: new Date(),
        id: generateId()
    };
}

function generateId() {
    return Math.random().toString(36).substr(2, 9);
}
EOF

# Create sample Python project
cat > demo_workspace/python_project/analyzer.py << 'EOF'
import os
import sys
import json
import asyncio
from typing import List, Dict, Optional, Union, Any
from dataclasses import dataclass
from enum import Enum

# Complex class with high cyclomatic complexity
class DataProcessor:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.stats = {'processed': 0, 'errors': 0, 'skipped': 0}

    def process_data_batch(self, data_batch: List[Dict[str, Any]]) -> Dict[str, List[Any]]:
        """Process a batch of data with complex business logic."""
        results = {'success': [], 'errors': [], 'warnings': []}

        for item in data_batch:
            try:
                if not item or not isinstance(item, dict):
                    self.stats['skipped'] += 1
                    continue

                # Deep nested processing logic
                if 'type' in item:
                    if item['type'] == 'user':
                        if 'profile' in item:
                            if item['profile'].get('status') == 'active':
                                if item['profile'].get('subscription', {}).get('tier') == 'premium':
                                    # Premium user processing
                                    if item.get('data', {}).get('usage', 0) > self.config.get('premium_threshold', 1000):
                                        processed = self._process_premium_user(item)
                                        if processed:
                                            results['success'].append(processed)
                                        else:
                                            results['warnings'].append({'item': item['id'], 'reason': 'premium_processing_failed'})
                                    else:
                                        results['success'].append(self._process_standard_user(item))
                                elif item['profile'].get('subscription', {}).get('tier') == 'standard':
                                    # Standard user processing
                                    if item.get('data', {}).get('usage', 0) > self.config.get('standard_threshold', 500):
                                        results['warnings'].append({'item': item['id'], 'reason': 'usage_limit_approaching'})
                                    results['success'].append(self._process_standard_user(item))
                                else:
                                    # Free tier processing
                                    if item.get('data', {}).get('usage', 0) > self.config.get('free_threshold', 100):
                                        results['errors'].append({'item': item['id'], 'reason': 'free_tier_limit_exceeded'})
                                    else:
                                        results['success'].append(self._process_free_user(item))
                            else:
                                # Inactive user
                                self.stats['skipped'] += 1
                                continue
                        else:
                            results['errors'].append({'item': item.get('id', 'unknown'), 'reason': 'missing_profile'})
                    elif item['type'] == 'organization':
                        if 'settings' in item:
                            if item['settings'].get('active', False):
                                # Organization processing
                                for member in item.get('members', []):
                                    if member.get('role') == 'admin':
                                        if member.get('permissions', {}).get('billing', False):
                                            # Process billing admin
                                            processed = self._process_billing_admin(member, item)
                                            if processed:
                                                results['success'].append(processed)
                                        elif member.get('permissions', {}).get('management', False):
                                            # Process management admin
                                            results['success'].append(self._process_management_admin(member, item))
                                    elif member.get('role') == 'user':
                                        results['success'].append(self._process_org_user(member, item))
                            else:
                                self.stats['skipped'] += 1
                        else:
                            results['errors'].append({'item': item.get('id', 'unknown'), 'reason': 'missing_settings'})
                    else:
                        results['errors'].append({'item': item.get('id', 'unknown'), 'reason': 'unknown_type'})
                else:
                    results['errors'].append({'item': item.get('id', 'unknown'), 'reason': 'missing_type'})

                self.stats['processed'] += 1

            except Exception as e:
                self.stats['errors'] += 1
                results['errors'].append({'item': item.get('id', 'unknown'), 'reason': str(e)})

        return results

    def _process_premium_user(self, user: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        # Premium user processing logic
        return {'id': user['id'], 'tier': 'premium', 'processed': True}

    def _process_standard_user(self, user: Dict[str, Any]) -> Dict[str, Any]:
        # Standard user processing logic
        return {'id': user['id'], 'tier': 'standard', 'processed': True}

    def _process_free_user(self, user: Dict[str, Any]) -> Dict[str, Any]:
        # Free user processing logic
        return {'id': user['id'], 'tier': 'free', 'processed': True}

    def _process_billing_admin(self, member: Dict[str, Any], org: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        # Billing admin processing
        return {'id': member['id'], 'org': org['id'], 'role': 'billing_admin', 'processed': True}

    def _process_management_admin(self, member: Dict[str, Any], org: Dict[str, Any]) -> Dict[str, Any]:
        # Management admin processing
        return {'id': member['id'], 'org': org['id'], 'role': 'management_admin', 'processed': True}

    def _process_org_user(self, member: Dict[str, Any], org: Dict[str, Any]) -> Dict[str, Any]:
        # Organization user processing
        return {'id': member['id'], 'org': org['id'], 'role': 'user', 'processed': True}

# Function with security risks
def dangerous_exec(user_code: str) -> Any:
    """Execute user-provided code - SECURITY RISK!"""
    return exec(user_code)  # 🚨 Code injection vulnerability

def unsafe_file_access(filename: str) -> str:
    """Read file without validation - SECURITY RISK!"""
    with open(filename, 'r') as f:  # 🚨 Path traversal vulnerability
        return f.read()

# Recursive function
def factorial(n: int) -> int:
    if n <= 1:
        return 1
    return n * factorial(n - 1)

# Async function with complex error handling
async def fetch_and_aggregate_data(urls: List[str], max_concurrent: int = 5) -> Dict[str, Any]:
    """Fetch data from multiple URLs and aggregate results."""
    semaphore = asyncio.Semaphore(max_concurrent)
    results = {'successful': [], 'failed': [], 'summary': {}}

    async def fetch_single_url(url: str) -> Dict[str, Any]:
        async with semaphore:
            try:
                # Simulate HTTP request
                await asyncio.sleep(0.1)  # Simulate network delay

                if 'error' in url:
                    raise Exception(f"Simulated error for {url}")

                return {'url': url, 'status': 'success', 'data': {'value': len(url)}}

            except Exception as e:
                return {'url': url, 'status': 'error', 'error': str(e)}

    # Execute all requests concurrently
    tasks = [fetch_single_url(url) for url in urls]
    responses = await asyncio.gather(*tasks, return_exceptions=True)

    # Process results
    for response in responses:
        if isinstance(response, Exception):
            results['failed'].append({'error': str(response)})
        elif response['status'] == 'success':
            results['successful'].append(response)
        else:
            results['failed'].append(response)

    # Generate summary
    results['summary'] = {
        'total_urls': len(urls),
        'successful': len(results['successful']),
        'failed': len(results['failed']),
        'success_rate': len(results['successful']) / len(urls) if urls else 0
    }

    return results
EOF

print_success "Demo workspace created successfully!"
echo

# Run analysis on each project
print_step "Running analysis on demo projects..."

echo
print_info "Analyzing Rust project..."
./target/release/codemetrics demo_workspace/rust_project --format json --output demo_workspace/rust_analysis.json
print_success "Rust analysis completed!"

echo
print_info "Analyzing JavaScript project..."
./target/release/codemetrics demo_workspace/js_project --format json --output demo_workspace/js_analysis.json
print_success "JavaScript analysis completed!"

echo
print_info "Analyzing Python project..."
./target/release/codemetrics demo_workspace/python_project --format json --output demo_workspace/python_analysis.json
print_success "Python analysis completed!"

echo
print_info "Analyzing mixed project (all languages)..."
./target/release/codemetrics demo_workspace --format table --metrics complexity,duplication,maintainability
print_success "Mixed project analysis completed!"

echo
print_step "Running specialized analysis demos..."

echo
print_info "Security-focused analysis on JavaScript..."
./target/release/codemetrics demo_workspace/js_project --metrics security --format table

echo
print_info "Complexity hotspot analysis..."
./target/release/codemetrics demo_workspace --format table --metrics complexity | head -20

echo
print_info "Generating HTML report..."
./target/release/codemetrics demo_workspace --format html --output demo_workspace/full_report.html
print_success "HTML report generated at demo_workspace/full_report.html"

echo
print_step "Performance benchmark..."

# Create a larger test project for performance testing
mkdir -p demo_workspace/large_project
for i in {1..50}; do
    cp demo_workspace/rust_project/main.rs demo_workspace/large_project/file_$i.rs
done

echo "Created large project with 50 files for performance testing..."

time ./target/release/codemetrics demo_workspace/large_project --format table --metrics all

print_success "Performance benchmark completed!"

echo
print_step "Cleanup and summary..."

echo
echo "📊 Demo Results Summary:"
echo "========================"
echo

if [[ -f demo_workspace/rust_analysis.json ]]; then
    print_success "Rust analysis: $(wc -l < demo_workspace/rust_analysis.json) lines of JSON output"
fi

if [[ -f demo_workspace/js_analysis.json ]]; then
    print_success "JavaScript analysis: $(wc -l < demo_workspace/js_analysis.json) lines of JSON output"
fi

if [[ -f demo_workspace/python_analysis.json ]]; then
    print_success "Python analysis: $(wc -l < demo_workspace/python_analysis.json) lines of JSON output"
fi

if [[ -f demo_workspace/full_report.html ]]; then
    print_success "HTML report generated successfully"
fi

echo
print_step "Key features demonstrated:"
echo "  🎯 Multi-language support (Rust, JavaScript, Python)"
echo "  🔍 AST-based analysis using tree-sitter"
echo "  🔒 Security pattern detection"
echo "  📊 Complexity analysis and hotspot identification"
echo "  📈 Multiple output formats (JSON, Table, HTML)"
echo "  ⚡ High-performance analysis (50 files in seconds)"
echo "  🎨 Rich visualization and reporting"

echo
print_success "🎉 Demo completed successfully!"
print_info "Check the demo_workspace/ directory for all generated reports and analysis files."

# Optional: Open HTML report if available
if command -v xdg-open >/dev/null 2>&1 && [[ -f demo_workspace/full_report.html ]]; then
    print_info "Opening HTML report in browser..."
    xdg-open demo_workspace/full_report.html
elif command -v open >/dev/null 2>&1 && [[ -f demo_workspace/full_report.html ]]; then
    print_info "Opening HTML report in browser..."
    open demo_workspace/full_report.html
fi

echo
echo "To run manual analysis, use:"
echo "  ./target/release/codemetrics [PATH] [OPTIONS]"
echo
echo "Example commands:"
echo "  ./target/release/codemetrics src/ --format table"
echo "  ./target/release/codemetrics . --metrics complexity --format json --output report.json"
echo "  ./target/release/codemetrics project/ --format html --output report.html"