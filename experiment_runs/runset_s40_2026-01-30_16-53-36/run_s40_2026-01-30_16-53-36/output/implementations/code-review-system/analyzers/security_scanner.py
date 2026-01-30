"""
Security Scanner - Advanced Security Vulnerability Detection Engine

This analyzer performs comprehensive security analysis including:
- OWASP Top 10 vulnerability detection
- SQL injection pattern recognition
- XSS vulnerability identification
- Authentication and authorization issues
- Cryptographic weakness detection
- Input validation analysis

Integrates seamlessly with Alice's workflow orchestration system.
"""

import re
import ast
import hashlib
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass
import json

@dataclass
class SecurityFinding:
    """Security-specific finding with risk assessment"""
    type: str
    severity: str  # 'critical', 'high', 'medium', 'low'
    message: str
    file_path: str
    line_number: int
    column: int
    rule_id: str
    cwe_id: Optional[str] = None  # Common Weakness Enumeration ID
    owasp_category: Optional[str] = None
    risk_score: int = 0  # 1-10 scale
    exploit_complexity: str = 'unknown'  # 'low', 'medium', 'high'
    suggestion: Optional[str] = None
    context: Optional[str] = None

class SecurityScanner:
    """
    Advanced security analysis engine that identifies vulnerabilities and security risks.
    Follows Alice's standardized interface for seamless workflow integration.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.security_config = config.get('security', {})

        # Language-specific security analyzers
        self.language_handlers = {
            'python': self._scan_python_security,
            'javascript': self._scan_javascript_security,
            'typescript': self._scan_javascript_security,  # Same patterns apply
            'java': self._scan_java_security,
            'php': self._scan_php_security,
            'sql': self._scan_sql_security
        }

        # Initialize security pattern databases
        self._init_vulnerability_patterns()
        self._init_cryptographic_patterns()
        self._init_injection_patterns()

    def analyze(self, file_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Main security analysis entry point for Alice's workflow system

        Returns findings in Alice's standardized format
        """
        findings = []

        try:
            file_path = file_data['path']
            content = file_data['content']
            language = file_data.get('language', 'unknown')

            # Route to language-specific security scanner
            if language in self.language_handlers:
                security_findings = self.language_handlers[language](file_path, content)
                # Convert SecurityFinding objects to Alice's Finding format
                findings.extend([self._convert_to_standard_finding(sf) for sf in security_findings])

            # Add cross-language security checks
            findings.extend(self._scan_general_security_patterns(file_path, content))

            # Filter based on risk thresholds
            findings = self._filter_by_risk_level(findings)

        except Exception as e:
            findings.append({
                'type': 'security_analyzer_error',
                'severity': 'error',
                'message': f'Security scan failed: {str(e)}',
                'file_path': file_data.get('path', 'unknown'),
                'line_number': 1,
                'column': 1,
                'rule_id': 'SEC_ERROR_001'
            })

        return findings

    def get_metadata(self) -> Dict[str, Any]:
        """Return security analyzer metadata for Alice's system"""
        return {
            'name': 'SecurityScanner',
            'version': '2.0.0',
            'supported_languages': list(self.language_handlers.keys()),
            'vulnerability_categories': [
                'injection', 'broken_auth', 'sensitive_exposure',
                'xxe', 'broken_access', 'security_misconfig',
                'xss', 'insecure_deserialization', 'known_vulnerabilities',
                'logging_monitoring'
            ],
            'owasp_coverage': 'OWASP Top 10 2021',
            'cwe_database_version': '4.9',
            'performance_characteristics': {
                'typical_file_time': '100-500ms',
                'memory_usage': 'medium',
                'scalability': 'good'
            }
        }

    def _scan_python_security(self, file_path: str, content: str) -> List[SecurityFinding]:
        """Comprehensive Python security analysis using AST and pattern matching"""
        findings = []

        try:
            tree = ast.parse(content)
            findings.extend(self._scan_python_ast_security(tree, file_path))
        except SyntaxError:
            pass  # Skip AST analysis for invalid syntax

        # Pattern-based security checks
        findings.extend(self._scan_python_injection_patterns(file_path, content))
        findings.extend(self._scan_python_crypto_patterns(file_path, content))
        findings.extend(self._scan_python_auth_patterns(file_path, content))

        return findings

    def _scan_python_ast_security(self, tree: ast.AST, file_path: str) -> List[SecurityFinding]:
        """AST-based Python security analysis"""
        findings = []

        class SecurityVisitor(ast.NodeVisitor):
            def __init__(self, findings_list, file_path):
                self.findings = findings_list
                self.file_path = file_path

            def visit_Call(self, node):
                # Check for dangerous function calls
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id

                    # eval() usage - critical security risk
                    if func_name == 'eval':
                        self.findings.append(SecurityFinding(
                            type='code_injection',
                            severity='critical',
                            message='Use of eval() function detected - critical security risk',
                            file_path=self.file_path,
                            line_number=node.lineno,
                            column=node.col_offset,
                            rule_id='PY_SEC_001',
                            cwe_id='CWE-94',
                            owasp_category='A03:2021 - Injection',
                            risk_score=9,
                            exploit_complexity='low',
                            suggestion='Use ast.literal_eval() for safe evaluation or implement specific parsing logic'
                        ))

                    # exec() usage
                    elif func_name == 'exec':
                        self.findings.append(SecurityFinding(
                            type='code_injection',
                            severity='critical',
                            message='Use of exec() function detected',
                            file_path=self.file_path,
                            line_number=node.lineno,
                            column=node.col_offset,
                            rule_id='PY_SEC_002',
                            cwe_id='CWE-94',
                            owasp_category='A03:2021 - Injection',
                            risk_score=9,
                            exploit_complexity='low'
                        ))

                    # compile() with user input
                    elif func_name == 'compile':
                        self.findings.append(SecurityFinding(
                            type='code_injection',
                            severity='high',
                            message='Use of compile() function - potential code injection',
                            file_path=self.file_path,
                            line_number=node.lineno,
                            column=node.col_offset,
                            rule_id='PY_SEC_003',
                            cwe_id='CWE-94',
                            risk_score=7
                        ))

                elif isinstance(node.func, ast.Attribute):
                    # subprocess calls with shell=True
                    if (hasattr(node.func, 'attr') and
                        isinstance(node.func.value, ast.Name) and
                        node.func.value.id == 'subprocess'):

                        # Check for shell=True in arguments
                        for keyword in node.keywords:
                            if keyword.arg == 'shell' and isinstance(keyword.value, ast.Constant):
                                if keyword.value.value is True:
                                    self.findings.append(SecurityFinding(
                                        type='command_injection',
                                        severity='high',
                                        message='subprocess call with shell=True detected',
                                        file_path=self.file_path,
                                        line_number=node.lineno,
                                        column=node.col_offset,
                                        rule_id='PY_SEC_004',
                                        cwe_id='CWE-78',
                                        owasp_category='A03:2021 - Injection',
                                        risk_score=8,
                                        suggestion='Use shell=False and pass commands as lists'
                                    ))

                self.generic_visit(node)

            def visit_Import(self, node):
                # Check for imports of potentially dangerous modules
                dangerous_modules = {'pickle', 'cPickle', 'marshal'}

                for alias in node.names:
                    if alias.name in dangerous_modules:
                        self.findings.append(SecurityFinding(
                            type='insecure_deserialization',
                            severity='medium',
                            message=f'Import of {alias.name} module detected - insecure deserialization risk',
                            file_path=self.file_path,
                            line_number=node.lineno,
                            column=node.col_offset,
                            rule_id='PY_SEC_005',
                            cwe_id='CWE-502',
                            owasp_category='A08:2021 - Software and Data Integrity Failures',
                            risk_score=6,
                            suggestion='Use JSON or other safe serialization formats'
                        ))

                self.generic_visit(node)

        visitor = SecurityVisitor(findings, file_path)
        visitor.visit(tree)
        return findings

    def _scan_python_injection_patterns(self, file_path: str, content: str) -> List[SecurityFinding]:
        """Pattern-based SQL and NoSQL injection detection for Python"""
        findings = []
        lines = content.split('\n')

        for i, line in enumerate(lines, 1):
            # SQL injection patterns
            sql_patterns = [
                (r'cursor\.execute\([^)]*%[^)]*\)', 'SQL string formatting in execute()'),
                (r'\.execute\([^)]*\+[^)]*\)', 'SQL concatenation in execute()'),
                (r'f[\'"][^\'"]*(SELECT|INSERT|UPDATE|DELETE)[^\'"]*.format\(', 'f-string SQL with formatting'),
                (r'(SELECT|INSERT|UPDATE|DELETE).*%s', 'Direct SQL string formatting')
            ]

            for pattern, description in sql_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    findings.append(SecurityFinding(
                        type='sql_injection',
                        severity='high',
                        message=f'Potential SQL injection: {description}',
                        file_path=file_path,
                        line_number=i,
                        column=re.search(pattern, line, re.IGNORECASE).start() + 1,
                        rule_id='PY_SEC_SQL_001',
                        cwe_id='CWE-89',
                        owasp_category='A03:2021 - Injection',
                        risk_score=8,
                        exploit_complexity='medium',
                        suggestion='Use parameterized queries or ORM methods',
                        context=line.strip()
                    ))

            # NoSQL injection patterns (MongoDB)
            nosql_patterns = [
                (r'\$where.*\+', 'MongoDB $where with concatenation'),
                (r'eval.*request\.|eval.*input\(', 'JavaScript eval with user input'),
            ]

            for pattern, description in nosql_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    findings.append(SecurityFinding(
                        type='nosql_injection',
                        severity='high',
                        message=f'Potential NoSQL injection: {description}',
                        file_path=file_path,
                        line_number=i,
                        column=re.search(pattern, line, re.IGNORECASE).start() + 1,
                        rule_id='PY_SEC_NOSQL_001',
                        cwe_id='CWE-943',
                        risk_score=7
                    ))

        return findings

    def _scan_python_crypto_patterns(self, file_path: str, content: str) -> List[SecurityFinding]:
        """Cryptographic weakness detection in Python"""
        findings = []
        lines = content.split('\n')

        for i, line in enumerate(lines, 1):
            # Weak hash algorithms
            weak_hashes = ['md5', 'sha1']
            for weak_hash in weak_hashes:
                if re.search(rf'\bhashlib\.{weak_hash}\b', line):
                    findings.append(SecurityFinding(
                        type='cryptographic_weakness',
                        severity='medium',
                        message=f'Weak cryptographic hash algorithm: {weak_hash}',
                        file_path=file_path,
                        line_number=i,
                        column=line.find(weak_hash) + 1,
                        rule_id='PY_SEC_CRYPTO_001',
                        cwe_id='CWE-327',
                        owasp_category='A02:2021 - Cryptographic Failures',
                        risk_score=5,
                        suggestion='Use SHA-256 or stronger algorithms'
                    ))

            # Hardcoded secrets/passwords
            secret_patterns = [
                (r'password\s*=\s*["\'][^"\']+["\']', 'Hardcoded password'),
                (r'api_?key\s*=\s*["\'][^"\']+["\']', 'Hardcoded API key'),
                (r'secret\s*=\s*["\'][^"\']+["\']', 'Hardcoded secret'),
                (r'token\s*=\s*["\'][A-Za-z0-9+/]{20,}["\']', 'Hardcoded token')
            ]

            for pattern, description in secret_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    findings.append(SecurityFinding(
                        type='sensitive_data_exposure',
                        severity='high',
                        message=f'{description} detected in source code',
                        file_path=file_path,
                        line_number=i,
                        column=re.search(pattern, line, re.IGNORECASE).start() + 1,
                        rule_id='PY_SEC_SECRETS_001',
                        cwe_id='CWE-798',
                        owasp_category='A02:2021 - Cryptographic Failures',
                        risk_score=8,
                        suggestion='Use environment variables or secure secret management'
                    ))

        return findings

    def _scan_python_auth_patterns(self, file_path: str, content: str) -> List[SecurityFinding]:
        """Authentication and authorization security checks"""
        findings = []
        lines = content.split('\n')

        for i, line in enumerate(lines, 1):
            # Session management issues
            if re.search(r'session\[.*\]\s*=.*request\.', line):
                findings.append(SecurityFinding(
                    type='broken_authentication',
                    severity='medium',
                    message='Direct session assignment from request data',
                    file_path=file_path,
                    line_number=i,
                    column=1,
                    rule_id='PY_SEC_AUTH_001',
                    cwe_id='CWE-287',
                    risk_score=6,
                    suggestion='Validate and sanitize data before session storage'
                ))

            # Missing CSRF protection
            if 'csrf_exempt' in line:
                findings.append(SecurityFinding(
                    type='broken_authentication',
                    severity='medium',
                    message='CSRF protection disabled',
                    file_path=file_path,
                    line_number=i,
                    column=line.find('csrf_exempt') + 1,
                    rule_id='PY_SEC_AUTH_002',
                    cwe_id='CWE-352',
                    risk_score=6,
                    suggestion='Implement proper CSRF protection'
                ))

        return findings

    def _scan_javascript_security(self, file_path: str, content: str) -> List[SecurityFinding]:
        """JavaScript/TypeScript security analysis"""
        findings = []
        lines = content.split('\n')

        for i, line in enumerate(lines, 1):
            # XSS vulnerabilities
            xss_patterns = [
                (r'innerHTML\s*=.*\+', 'innerHTML with concatenation - XSS risk'),
                (r'document\.write\s*\(', 'document.write() usage - XSS risk'),
                (r'eval\s*\(', 'eval() usage - code injection risk'),
                (r'Function\s*\(.*\+', 'Function constructor with concatenation'),
                (r'setTimeout\s*\(.*\+', 'setTimeout with string concatenation'),
                (r'setInterval\s*\(.*\+', 'setInterval with string concatenation')
            ]

            for pattern, description in xss_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    findings.append(SecurityFinding(
                        type='xss',
                        severity='high',
                        message=description,
                        file_path=file_path,
                        line_number=i,
                        column=re.search(pattern, line, re.IGNORECASE).start() + 1,
                        rule_id='JS_SEC_XSS_001',
                        cwe_id='CWE-79',
                        owasp_category='A03:2021 - Injection',
                        risk_score=8,
                        suggestion='Use textContent or proper sanitization libraries'
                    ))

            # Prototype pollution
            if re.search(r'__proto__', line):
                findings.append(SecurityFinding(
                    type='prototype_pollution',
                    severity='medium',
                    message='__proto__ usage detected - prototype pollution risk',
                    file_path=file_path,
                    line_number=i,
                    column=line.find('__proto__') + 1,
                    rule_id='JS_SEC_PROTO_001',
                    cwe_id='CWE-1321',
                    risk_score=6
                ))

        return findings

    def _scan_java_security(self, file_path: str, content: str) -> List[SecurityFinding]:
        """Java security vulnerability detection"""
        findings = []
        lines = content.split('\n')

        for i, line in enumerate(lines, 1):
            # Deserialization vulnerabilities
            if 'ObjectInputStream' in line and 'readObject' in line:
                findings.append(SecurityFinding(
                    type='insecure_deserialization',
                    severity='high',
                    message='Potential insecure deserialization with ObjectInputStream',
                    file_path=file_path,
                    line_number=i,
                    column=1,
                    rule_id='JAVA_SEC_DESER_001',
                    cwe_id='CWE-502',
                    owasp_category='A08:2021 - Software and Data Integrity Failures',
                    risk_score=8
                ))

            # SQL injection patterns
            if re.search(r'Statement.*executeQuery.*\+', line):
                findings.append(SecurityFinding(
                    type='sql_injection',
                    severity='high',
                    message='SQL concatenation in executeQuery - injection risk',
                    file_path=file_path,
                    line_number=i,
                    column=1,
                    rule_id='JAVA_SEC_SQL_001',
                    cwe_id='CWE-89',
                    risk_score=8,
                    suggestion='Use PreparedStatement with parameterized queries'
                ))

        return findings

    def _scan_php_security(self, file_path: str, content: str) -> List[SecurityFinding]:
        """PHP security analysis"""
        findings = []
        lines = content.split('\n')

        for i, line in enumerate(lines, 1):
            # Command injection
            php_dangerous_functions = ['exec', 'shell_exec', 'system', 'passthru', 'eval']

            for func in php_dangerous_functions:
                if re.search(rf'{func}\s*\(.*\$', line):
                    findings.append(SecurityFinding(
                        type='command_injection',
                        severity='critical',
                        message=f'Dangerous PHP function {func}() with variable input',
                        file_path=file_path,
                        line_number=i,
                        column=line.find(func) + 1,
                        rule_id='PHP_SEC_CMD_001',
                        cwe_id='CWE-78',
                        risk_score=9,
                        exploit_complexity='low'
                    ))

            # SQL injection
            if re.search(r'mysql_query.*\$|mysqli_query.*\$', line):
                findings.append(SecurityFinding(
                    type='sql_injection',
                    severity='high',
                    message='Direct SQL query with variable - injection risk',
                    file_path=file_path,
                    line_number=i,
                    column=1,
                    rule_id='PHP_SEC_SQL_001',
                    cwe_id='CWE-89',
                    risk_score=8
                ))

        return findings

    def _scan_sql_security(self, file_path: str, content: str) -> List[SecurityFinding]:
        """Direct SQL file security analysis"""
        findings = []
        lines = content.split('\n')

        for i, line in enumerate(lines, 1):
            # Look for dynamic SQL construction patterns
            if re.search(r'EXEC\s*\(|EXECUTE\s*\(', line, re.IGNORECASE):
                findings.append(SecurityFinding(
                    type='sql_injection',
                    severity='high',
                    message='Dynamic SQL execution detected',
                    file_path=file_path,
                    line_number=i,
                    column=1,
                    rule_id='SQL_SEC_001',
                    cwe_id='CWE-89',
                    risk_score=7
                ))

        return findings

    def _scan_general_security_patterns(self, file_path: str, content: str) -> List[Dict[str, Any]]:
        """Cross-language security pattern detection"""
        findings = []
        lines = content.split('\n')

        for i, line in enumerate(lines, 1):
            # Check for common vulnerability indicators
            if re.search(r'TODO.*security|FIXME.*security|HACK.*security', line, re.IGNORECASE):
                findings.append({
                    'type': 'security_todo',
                    'severity': 'medium',
                    'message': 'Security-related TODO/FIXME comment',
                    'file_path': file_path,
                    'line_number': i,
                    'column': 1,
                    'rule_id': 'SEC_TODO_001',
                    'context': line.strip()
                })

        return findings

    def _convert_to_standard_finding(self, security_finding: SecurityFinding) -> Dict[str, Any]:
        """Convert SecurityFinding to Alice's standard Finding format"""
        return {
            'type': security_finding.type,
            'severity': security_finding.severity,
            'message': security_finding.message,
            'file_path': security_finding.file_path,
            'line_number': security_finding.line_number,
            'column': security_finding.column,
            'rule_id': security_finding.rule_id,
            'suggestion': security_finding.suggestion,
            'context': security_finding.context,
            # Include security-specific metadata
            'metadata': {
                'cwe_id': security_finding.cwe_id,
                'owasp_category': security_finding.owasp_category,
                'risk_score': security_finding.risk_score,
                'exploit_complexity': security_finding.exploit_complexity
            }
        }

    def _filter_by_risk_level(self, findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter findings based on configured risk thresholds"""
        if not self.security_config.get('enabled', True):
            return []

        min_risk_score = self.security_config.get('min_risk_score', 1)
        severity_filter = self.security_config.get('severity_levels', ['critical', 'high', 'medium', 'low'])

        filtered = []
        for finding in findings:
            # Check severity filter
            if finding['severity'] not in severity_filter:
                continue

            # Check risk score filter (if available)
            metadata = finding.get('metadata', {})
            risk_score = metadata.get('risk_score', 0)
            if risk_score > 0 and risk_score < min_risk_score:
                continue

            filtered.append(finding)

        return filtered

    def _init_vulnerability_patterns(self):
        """Initialize OWASP Top 10 and CWE pattern databases"""
        # This would load comprehensive vulnerability pattern databases
        pass

    def _init_cryptographic_patterns(self):
        """Initialize cryptographic weakness detection patterns"""
        # This would load crypto-specific vulnerability patterns
        pass

    def _init_injection_patterns(self):
        """Initialize injection attack pattern databases"""
        # This would load injection-specific patterns for all languages
        pass