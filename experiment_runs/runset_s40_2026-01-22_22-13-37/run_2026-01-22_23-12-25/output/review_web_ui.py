#!/usr/bin/env python3
"""
Web UI for Smart Code Review Assistant
Simple Flask web interface for code review analysis

Usage:
    python review_web_ui.py
    Open http://localhost:5000 in your browser
"""

from flask import Flask, render_template_string, request, jsonify
import os
import tempfile
from smart_review_assistant import SmartReviewAnalyzer, format_smart_review_report

app = Flask(__name__)

# HTML template for the web interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Smart Code Review Assistant</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
        }
        .input-section {
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .diff-input {
            width: 100%;
            height: 300px;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            border: 2px solid #e1e1e1;
            border-radius: 5px;
            padding: 15px;
            resize: vertical;
        }
        .analyze-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 30px;
            font-size: 16px;
            border-radius: 5px;
            cursor: pointer;
            margin-top: 10px;
        }
        .analyze-btn:hover {
            opacity: 0.9;
        }
        .analyze-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        .results-section {
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            display: none;
        }
        .loading {
            text-align: center;
            font-style: italic;
            color: #666;
            display: none;
        }
        .error {
            background: #fee;
            border: 1px solid #fcc;
            padding: 15px;
            border-radius: 5px;
            color: #c00;
            display: none;
        }
        pre {
            background: #f8f8f8;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            white-space: pre-wrap;
            line-height: 1.4;
        }
        .example-btn {
            background: #28a745;
            color: white;
            border: none;
            padding: 8px 16px;
            font-size: 14px;
            border-radius: 3px;
            cursor: pointer;
            margin-left: 10px;
        }
        .example-btn:hover {
            background: #218838;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🔍 Smart Code Review Assistant</h1>
        <p>Analyze code changes and get intelligent review insights</p>
    </div>

    <div class="input-section">
        <h2>Paste Your Git Diff</h2>
        <p>Paste the output of <code>git diff</code> or <code>git show [commit]</code> below:</p>

        <textarea id="diffInput" class="diff-input"
                  placeholder="diff --git a/src/example.py b/src/example.py
index 1234567..abcdefg 100644
--- a/src/example.py
+++ b/src/example.py
@@ -10,6 +10,8 @@ def example_function():
     # Your git diff content here
+    new_line = 'added code'
     return result"></textarea>

        <br>
        <button id="analyzeBtn" class="analyze-btn" onclick="analyzeDiff()">
            🚀 Analyze Changes
        </button>
        <button class="example-btn" onclick="loadExample()">
            📝 Load Example
        </button>
    </div>

    <div id="loading" class="loading">
        Analyzing your code changes... This may take a moment.
    </div>

    <div id="error" class="error"></div>

    <div id="results" class="results-section">
        <h2>Review Analysis Results</h2>
        <pre id="analysisOutput"></pre>
    </div>

    <script>
        function loadExample() {
            const exampleDiff = `diff --git a/src/auth/user_manager.py b/src/auth/user_manager.py
index 1234567..abcdefg 100644
--- a/src/auth/user_manager.py
+++ b/src/auth/user_manager.py
@@ -15,6 +15,7 @@ class UserManager:
     def __init__(self, db_connection):
         self.db = db_connection
         self.cache = {}
+        self.rate_limiter = RateLimiter(max_requests=100)

     def authenticate(self, username, password):
         """Authenticate a user with username and password"""
@@ -23,8 +24,12 @@ class UserManager:
             return None

         # Hash the password and compare
-        hashed = hashlib.sha256(password.encode()).hexdigest()
-        return hashed == user['password']
+        if not self.rate_limiter.check_limit(username):
+            raise AuthenticationError("Rate limit exceeded")
+
+        hashed = hashlib.sha256(password.encode('utf-8')).hexdigest()
+        is_valid = hashed == user['password']
+        return is_valid

     def create_user(self, username, email, password):
         """Create a new user account"""
@@ -35,6 +40,9 @@ class UserManager:
         hashed_password = hashlib.sha256(password.encode()).hexdigest()

+        # Validate email format
+        if not self._validate_email(email):
+            raise ValueError("Invalid email format")
+
         user_data = {
             'username': username,
             'email': email,
@@ -44,3 +52,8 @@ class UserManager:

         self.db.insert('users', user_data)
         return True
+
+    def _validate_email(self, email):
+        """Validate email format using regex"""
+        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'
+        return re.match(pattern, email) is not None

diff --git a/tests/test_user_manager.py b/tests/test_user_manager.py
index 9876543..fedcba9 100644
--- a/tests/test_user_manager.py
+++ b/tests/test_user_manager.py
@@ -45,6 +45,18 @@ class TestUserManager(unittest.TestCase):
         result = self.user_manager.authenticate('testuser', 'wrongpassword')
         self.assertFalse(result)

+    def test_rate_limiting(self):
+        """Test that rate limiting works correctly"""
+        # Make 101 requests to trigger rate limit
+        for i in range(100):
+            self.user_manager.authenticate('testuser', 'testpass')
+
+        # This should raise an exception
+        with self.assertRaises(AuthenticationError):
+            self.user_manager.authenticate('testuser', 'testpass')
+
+        # Different user should still work
+        self.assertTrue(self.user_manager.authenticate('otheruser', 'otherpass'))

     def test_create_user_success(self):
         """Test successful user creation"""
@@ -60,6 +72,12 @@ class TestUserManager(unittest.TestCase):
         with self.assertRaises(ValueError):
             self.user_manager.create_user('', 'test@example.com', 'password')

+    def test_invalid_email_format(self):
+        """Test that invalid email formats are rejected"""
+        with self.assertRaises(ValueError):
+            self.user_manager.create_user('testuser', 'invalid-email', 'password')
+        with self.assertRaises(ValueError):
+            self.user_manager.create_user('testuser', 'test@', 'password')

 if __name__ == '__main__':
     unittest.main()`;

            document.getElementById('diffInput').value = exampleDiff;
        }

        async function analyzeDiff() {
            const diffContent = document.getElementById('diffInput').value.trim();

            if (!diffContent) {
                showError('Please paste a git diff to analyze.');
                return;
            }

            const analyzeBtn = document.getElementById('analyzeBtn');
            const loading = document.getElementById('loading');
            const results = document.getElementById('results');
            const error = document.getElementById('error');

            // Show loading state
            analyzeBtn.disabled = true;
            analyzeBtn.textContent = 'Analyzing...';
            loading.style.display = 'block';
            results.style.display = 'none';
            error.style.display = 'none';

            try {
                const response = await fetch('/analyze', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ diff: diffContent })
                });

                const data = await response.json();

                if (data.success) {
                    document.getElementById('analysisOutput').textContent = data.analysis;
                    results.style.display = 'block';
                } else {
                    showError(data.error || 'Analysis failed');
                }
            } catch (err) {
                showError('Network error: ' + err.message);
            } finally {
                // Reset button state
                analyzeBtn.disabled = false;
                analyzeBtn.textContent = '🚀 Analyze Changes';
                loading.style.display = 'none';
            }
        }

        function showError(message) {
            const error = document.getElementById('error');
            error.textContent = message;
            error.style.display = 'block';
        }

        // Allow Enter+Ctrl to submit
        document.getElementById('diffInput').addEventListener('keydown', function(e) {
            if (e.ctrlKey && e.key === 'Enter') {
                analyzeDiff();
            }
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Main page with diff input form"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/analyze', methods=['POST'])
def analyze():
    """Analyze the provided diff content"""
    try:
        data = request.get_json()
        if not data or 'diff' not in data:
            return jsonify({'success': False, 'error': 'No diff content provided'})

        diff_content = data['diff']
        if not diff_content.strip():
            return jsonify({'success': False, 'error': 'Diff content is empty'})

        # Create analyzer and process the diff
        analyzer = SmartReviewAnalyzer()
        changes = analyzer.analyze_diff(diff_content, include_context=True)

        if not changes:
            return jsonify({'success': False, 'error': 'No analyzable changes found in the diff'})

        # Format the results
        report = format_smart_review_report(changes)

        return jsonify({
            'success': True,
            'analysis': report,
            'stats': {
                'files_changed': len(changes),
                'total_lines': sum(c.lines_added + c.lines_removed for c in changes),
                'average_complexity': sum(c.complexity_score for c in changes) / len(changes)
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'error': f'Analysis error: {str(e)}'})

if __name__ == '__main__':
    print("🚀 Starting Smart Code Review Assistant Web UI")
    print("📍 Open http://localhost:5000 in your browser")
    app.run(debug=True, host='0.0.0.0', port=5000)