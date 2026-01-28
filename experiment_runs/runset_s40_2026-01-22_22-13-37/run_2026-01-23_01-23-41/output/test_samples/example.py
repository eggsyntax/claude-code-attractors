"""Python example for code analysis"""

def fibonacci(n):
    """Simple recursive function"""
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

def complex_data_processing(data_list, options=None):
    """Function with higher complexity"""
    if not data_list:
        return []

    options = options or {}
    result = []

    for item in data_list:
        if isinstance(item, dict):
            if 'value' in item:
                if options.get('normalize', False):
                    if item['value'] > 100:
                        normalized = item['value'] / 100
                        if normalized > 10:
                            result.append({'processed': normalized, 'status': 'high'})
                        elif normalized > 5:
                            result.append({'processed': normalized, 'status': 'medium'})
                        else:
                            result.append({'processed': normalized, 'status': 'low'})
                    else:
                        result.append({'processed': item['value'], 'status': 'raw'})
                else:
                    result.append(item)
            elif 'error' in item:
                if options.get('skip_errors', True):
                    continue
                else:
                    result.append({'error': item['error'], 'status': 'error'})
        elif isinstance(item, (int, float)):
            result.append({'processed': item * 2, 'status': 'number'})
        else:
            if options.get('convert_strings', False):
                try:
                    converted = float(item)
                    result.append({'processed': converted, 'status': 'converted'})
                except ValueError:
                    if options.get('skip_invalid', True):
                        continue
                    else:
                        result.append({'error': f'Cannot convert {item}', 'status': 'error'})

    return result

class DataProcessor:
    """Class with various methods of different complexity"""

    def __init__(self, config):
        self.config = config
        self.cache = {}

    def simple_method(self, x, y):
        """Simple method - low complexity"""
        return x + y

    def process_with_cache(self, key, data):
        """Method with caching logic"""
        if key in self.cache:
            cached_result = self.cache[key]
            if cached_result['timestamp'] > self.get_current_time() - 3600:
                return cached_result['value']
            else:
                del self.cache[key]

        processed = self.heavy_processing(data)
        self.cache[key] = {
            'value': processed,
            'timestamp': self.get_current_time()
        }
        return processed

    def heavy_processing(self, data):
        """Simulate complex processing"""
        import time
        time.sleep(0.1)
        return sum(data) if isinstance(data, list) else data

    def get_current_time(self):
        """Simple helper method"""
        import time
        return time.time()