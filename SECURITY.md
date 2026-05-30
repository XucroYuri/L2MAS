# Security Policy

## Supported Versions

This repository is currently an early prototype. Security fixes target the `main` branch unless release branches are introduced later.

## Reporting a Vulnerability

Please do not open a public issue for suspected vulnerabilities, leaked credentials, unsafe defaults, or private endpoint exposure.

Use GitHub private vulnerability reporting when it is enabled for the repository. If it is not enabled yet, contact the maintainers privately through the project owner's preferred GitHub contact path and include:

- affected files, services, or configuration
- reproduction steps
- expected impact
- suggested mitigation, if known

We will acknowledge valid reports when maintainers are available and coordinate disclosure before publishing details.

## Security Expectations

- Do not commit real API keys, tokens, cookies, private endpoints, model licenses, or private model weights.
- Use `.env` for local secrets and keep `.env.example` limited to placeholders.
- Change all default passwords before running public or shared deployments.
- Treat local model endpoints as privileged services if they can read files, call tools, or access private networks.
- Review provider terms before routing user prompts, voices, images, or generated assets to third-party services.
