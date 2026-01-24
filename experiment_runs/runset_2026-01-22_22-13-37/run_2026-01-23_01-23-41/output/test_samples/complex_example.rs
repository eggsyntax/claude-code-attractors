// A complex Rust file to test our analyzer
use std::collections::HashMap;
use std::sync::Arc;

/// User management service with various complexity patterns
pub struct UserService {
    users: HashMap<u64, User>,
    cache: Arc<HashMap<String, String>>,
}

#[derive(Debug, Clone)]
pub struct User {
    id: u64,
    name: String,
    email: String,
    role: UserRole,
    metadata: HashMap<String, String>,
}

#[derive(Debug, Clone, PartialEq)]
pub enum UserRole {
    Admin,
    Moderator,
    User,
    Guest,
}

impl UserService {
    pub fn new() -> Self {
        Self {
            users: HashMap::new(),
            cache: Arc::new(HashMap::new()),
        }
    }

    // This function has high complexity - nested conditions and loops
    pub fn validate_and_process_user(&mut self, user_data: &str, options: ProcessingOptions) -> Result<User, UserError> {
        if user_data.is_empty() {
            return Err(UserError::InvalidInput("Empty user data".to_string()));
        }

        let parsed_data = if user_data.starts_with("{") {
            if user_data.ends_with("}") {
                match serde_json::from_str::<UserData>(user_data) {
                    Ok(data) => data,
                    Err(_) => {
                        if options.fallback_parsing {
                            self.fallback_parse(user_data)?
                        } else {
                            return Err(UserError::ParseError("JSON parsing failed".to_string()));
                        }
                    }
                }
            } else {
                return Err(UserError::InvalidFormat("Malformed JSON".to_string()));
            }
        } else if user_data.starts_with("user:") {
            self.parse_legacy_format(user_data)?
        } else {
            return Err(UserError::UnknownFormat);
        };

        // Multiple validation loops with nested conditions
        for field in &parsed_data.required_fields {
            if field.is_empty() {
                return Err(UserError::EmptyField(field.clone()));
            }

            if field.len() > 100 {
                if options.truncate_long_fields {
                    // Complex nested processing
                    for (i, chunk) in field.chars().collect::<Vec<_>>().chunks(50).enumerate() {
                        if i > 2 {
                            break;
                        }
                        let chunk_str: String = chunk.iter().collect();
                        if !chunk_str.chars().all(|c| c.is_alphanumeric() || c.is_whitespace()) {
                            if options.strict_validation {
                                return Err(UserError::InvalidCharacters(chunk_str));
                            } else {
                                // Sanitize the chunk
                                let sanitized = chunk_str
                                    .chars()
                                    .filter(|c| c.is_alphanumeric() || c.is_whitespace())
                                    .collect::<String>();
                                if sanitized.len() < chunk_str.len() / 2 {
                                    return Err(UserError::TooManyInvalidCharacters);
                                }
                            }
                        }
                    }
                } else {
                    return Err(UserError::FieldTooLong(field.clone()));
                }
            }
        }

        // Role assignment with complex logic
        let role = match parsed_data.role.as_deref() {
            Some("admin") => {
                if self.can_assign_admin_role(&parsed_data.email) {
                    if self.verify_admin_permissions(&parsed_data) {
                        UserRole::Admin
                    } else {
                        UserRole::Moderator
                    }
                } else {
                    UserRole::User
                }
            }
            Some("mod") | Some("moderator") => {
                if self.can_assign_moderator_role(&parsed_data.email) {
                    UserRole::Moderator
                } else {
                    UserRole::User
                }
            }
            Some("user") | None => UserRole::User,
            Some("guest") => UserRole::Guest,
            Some(other) => {
                if options.unknown_roles_as_guest {
                    UserRole::Guest
                } else {
                    return Err(UserError::UnknownRole(other.to_string()));
                }
            }
        };

        // Create user with additional complexity
        let user = User {
            id: self.generate_user_id(),
            name: parsed_data.name.clone(),
            email: parsed_data.email.clone(),
            role,
            metadata: self.build_metadata(&parsed_data, &options)?,
        };

        // Final validation and storage
        if let Err(e) = self.validate_user_constraints(&user) {
            if options.fix_constraint_violations {
                let fixed_user = self.fix_user_constraints(user)?;
                self.users.insert(fixed_user.id, fixed_user.clone());
                Ok(fixed_user)
            } else {
                Err(e)
            }
        } else {
            self.users.insert(user.id, user.clone());
            Ok(user)
        }
    }

    // Another complex function with deep nesting
    fn can_assign_admin_role(&self, email: &str) -> bool {
        if email.contains("@") {
            let parts: Vec<&str> = email.split("@").collect();
            if parts.len() == 2 {
                let domain = parts[1];
                if domain == "company.com" {
                    if email.starts_with("admin.") {
                        true
                    } else if email.starts_with("super.") {
                        true
                    } else {
                        false
                    }
                } else if domain == "trusted-partner.com" {
                    true
                } else {
                    false
                }
            } else {
                false
            }
        } else {
            false
        }
    }

    fn generate_user_id(&mut self) -> u64 {
        // Simple function - low complexity
        self.users.len() as u64 + 1
    }
}

// Supporting types and structs
#[derive(Debug)]
pub struct ProcessingOptions {
    pub fallback_parsing: bool,
    pub truncate_long_fields: bool,
    pub strict_validation: bool,
    pub unknown_roles_as_guest: bool,
    pub fix_constraint_violations: bool,
}

#[derive(Debug, serde::Deserialize)]
struct UserData {
    name: String,
    email: String,
    role: Option<String>,
    required_fields: Vec<String>,
}

#[derive(Debug, thiserror::Error)]
pub enum UserError {
    #[error("Invalid input: {0}")]
    InvalidInput(String),
    #[error("Parse error: {0}")]
    ParseError(String),
    #[error("Invalid format: {0}")]
    InvalidFormat(String),
    #[error("Unknown format")]
    UnknownFormat,
    #[error("Empty field: {0}")]
    EmptyField(String),
    #[error("Field too long: {0}")]
    FieldTooLong(String),
    #[error("Invalid characters: {0}")]
    InvalidCharacters(String),
    #[error("Too many invalid characters")]
    TooManyInvalidCharacters,
    #[error("Unknown role: {0}")]
    UnknownRole(String),
    #[error("Constraint violation")]
    ConstraintViolation,
}

// Implementation stubs to make it compile
impl UserService {
    fn fallback_parse(&self, _data: &str) -> Result<UserData, UserError> {
        todo!()
    }

    fn parse_legacy_format(&self, _data: &str) -> Result<UserData, UserError> {
        todo!()
    }

    fn verify_admin_permissions(&self, _data: &UserData) -> bool {
        todo!()
    }

    fn can_assign_moderator_role(&self, _email: &str) -> bool {
        todo!()
    }

    fn build_metadata(&self, _data: &UserData, _options: &ProcessingOptions) -> Result<HashMap<String, String>, UserError> {
        todo!()
    }

    fn validate_user_constraints(&self, _user: &User) -> Result<(), UserError> {
        todo!()
    }

    fn fix_user_constraints(&self, _user: User) -> Result<User, UserError> {
        todo!()
    }
}