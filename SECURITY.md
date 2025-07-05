# Security Policy

## Supported Versions

We provide security updates for the following versions of SQL Generator:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| 0.9.x   | :x:                |
| < 0.9   | :x:                |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security vulnerability in SQL Generator, please follow these steps:

### 1. Do Not Create Public Issues

**Please do not report security vulnerabilities through public GitHub issues.** This could expose the vulnerability to malicious actors before we have a chance to fix it.

### 2. Contact Us Privately

Send your report to our security team:

- **Email**: mishantanupandit@gmail.com
- **Subject**: [SECURITY] Vulnerability Report in SQL Generator

### 3. Include Detailed Information

Please include the following information in your report:

- **Description** of the vulnerability
- **Steps to reproduce** the issue
- **Potential impact** of the vulnerability
- **Affected versions** (if known)
- **Your contact information** for follow-up questions
- **Proof of concept** code (if applicable)

### 4. What to Expect

- **Acknowledgment**: We will acknowledge receipt of your report within 24 hours
- **Investigation**: We will investigate the issue and determine its severity
- **Updates**: We will provide updates on our progress within 72 hours
- **Resolution**: We aim to resolve critical vulnerabilities within 7 days
- **Disclosure**: We will coordinate with you on responsible disclosure

## Security Measures

### Current Security Features

1. **Input Validation**
   - All user inputs are validated and sanitized
   - SQL injection prevention through parameterized queries
   - Path traversal protection for file operations

2. **Data Protection**
   - No sensitive data is logged
   - Configuration files can contain sensitive information - keep them secure
   - Vector embeddings contain only schema metadata, not actual data

3. **Dependency Security**
   - Regular dependency updates
   - Automated security scanning with GitHub security advisories
   - Minimal dependency footprint

### Known Security Considerations

1. **Schema Files**
   - Schema files may contain sensitive database structure information
   - Store schema files securely and limit access
   - Do not commit sensitive schema files to public repositories

2. **Configuration Files**
   - Configuration files may contain API keys or database credentials
   - Use environment variables for sensitive configuration
   - Add config files to `.gitignore`

3. **Vector Embeddings**
   - Embeddings are stored locally in ChromaDB
   - Ensure proper file system permissions on the data directory
   - Consider encryption at rest for sensitive environments

## Best Practices for Users

### 1. Secure Configuration

```json
// ❌ Don't do this - sensitive data in config
{
  "database": {
    "password": "secret123",
    "api_key": "sk-1234567890"
  }
}

// ✅ Do this - use environment variables
{
  "database": {
    "password": "${DB_PASSWORD}",
    "api_key": "${API_KEY}"
  }
}
```

### 2. File Permissions

```bash
# Set secure permissions on data directory
chmod 700 data/
chmod 600 data/config/config.json

# Ensure proper ownership
chown -R your_user:your_group data/
```

### 3. Schema Sanitization

```json
// ❌ Don't include sensitive information in descriptions
{
  "tables": {
    "users": {
      "description": "User table with SSN and credit card data",
      "columns": {
        "ssn": {
          "description": "Social Security Number - format: 123-45-6789"
        }
      }
    }
  }
}

// ✅ Use generic descriptions
{
  "tables": {
    "users": {
      "description": "User account information",
      "columns": {
        "ssn": {
          "description": "Social security identifier"
        }
      }
    }
  }
}
```

### 4. Environment Isolation

```bash
# Use virtual environments
python -m venv venv
source venv/bin/activate

# Use containers for production
docker run -v ./data:/app/data sql-generator:latest
```

## Vulnerability Response Process

### Severity Levels

| Severity | Description | Response Time |
|----------|-------------|---------------|
| **Critical** | Remote code execution, data breach | 24 hours |
| **High** | Privilege escalation, significant data exposure | 72 hours |
| **Medium** | Information disclosure, denial of service | 1 week |
| **Low** | Minor information leak, configuration issues | 2 weeks |

### Response Timeline

1. **T+0**: Vulnerability reported
2. **T+24h**: Acknowledgment and initial assessment
3. **T+72h**: Severity classification and impact analysis
4. **T+1 week**: Fix development and testing (critical/high)
5. **T+2 weeks**: Patch release and public disclosure

### Public Disclosure

- We follow responsible disclosure practices
- Public disclosure occurs after a fix is available
- Credit is given to security researchers (with permission)
- Security advisories are published on GitHub

## Security Advisories

Security advisories will be published on:

- [GitHub Security Advisories](https://github.com/shantanupandit/sql-generator/security/advisories)
- Project documentation
- Release notes

## Bounty Program

Currently, we do not offer a formal bug bounty program. However, we greatly appreciate security research and will:

- Acknowledge your contribution in our security hall of fame
- Provide a detailed written acknowledgment
- Consider feature requests from security researchers

## Security Contact

- **Email**: mishantanupandit@gmail.com
- **PGP Key**: [Available on request]
- **Response Time**: Within 24 hours

## Regular Security Practices

### Code Review

- All code changes require review
- Security-focused review for sensitive changes
- Automated security scanning in CI/CD

### Dependency Management

- Regular dependency updates
- Automated vulnerability scanning
- Minimal dependency principle

### Testing

- Security unit tests
- Integration tests for security features
- Regular security audits

### Documentation

- Security considerations in all documentation
- Regular updates to security practices
- User education on secure usage

## Compliance

This project aims to follow:

- OWASP Top 10 security guidelines
- Secure coding practices
- Industry-standard vulnerability disclosure

## Updates to This Policy

This security policy may be updated periodically. Users will be notified of significant changes through:

- GitHub releases
- Security advisories
- Project documentation updates

---

**Last Updated**: January 2025  
**Version**: 1.0  
**Next Review**: July 2025
