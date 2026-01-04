# Changelog

All notable changes to the Risk Influence Map project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-04

### Added - Initial Release

#### Core Features
- Interactive risk management dashboard
- Neo4j graph database integration
- Dynamic risk visualization using PyVis
- Full CRUD operations for risks and influences
- Four influence types: AMPLIFIES, TRIGGERS, MITIGATES, CORRELATES
- Risk scoring system (Probability × Impact)
- Eight risk categories (Cyber, Operational, Strategic, Financial, Compliance, Reputation, HR, Environmental)
- Real-time graph updates
- Basic analytics and statistics

#### Visualization
- Interactive network graph with zoom and pan
- Node sizing based on risk score
- Color coding by category or score
- Edge styling by influence type and strength
- Hover tooltips with risk details
- Configurable physics simulation

#### Data Management
- Demo dataset with 15 risks and 20+ influences
- Cypher scripts for data loading
- Docker Compose configuration for Neo4j

#### Documentation
- Comprehensive README with quick start guide
- Detailed USER_GUIDE with best practices
- Technical SETUP guide with troubleshooting
- CONTRIBUTING guidelines
- MIT License

#### Developer Experience
- Cross-platform startup scripts (Windows/Mac/Linux)
- Docker containerization for Neo4j
- Python virtual environment support
- Clear code structure and documentation
- Environment variable configuration support

### Technical Details

#### Stack
- Python 3.9+
- Streamlit 1.29+
- Neo4j 5.0+ (Docker)
- PyVis 0.3.2+
- Pandas 2.1+

#### Architecture
- Single-page Streamlit application
- Neo4j Bolt protocol for database communication
- Stateless design with session-based data loading
- Responsive UI with sidebar navigation

## [Unreleased]

### Fixed
- TypeError when risks have None values for score, probability, or impact
- TypeError when numeric fields are stored as strings in database
- FileNotFoundError on Windows due to hardcoded Linux paths
- Average score calculation now properly handles null values
- Edge width calculation handles None and string strength values
- Graph visualization now uses cross-platform temporary directory
- Added `safe_int()` utility function for robust type conversion

### Planned Features

#### High Priority
- [ ] CSV import/export for risks and influences
- [ ] Layout persistence for graph visualization
- [ ] Risk history and change tracking
- [ ] Automated backup functionality
- [ ] User authentication and authorization
- [ ] Advanced filtering and search
- [ ] Risk scenario comparison
- [ ] PDF report generation

#### Medium Priority
- [ ] REST API for external integrations
- [ ] Risk framework integration (EBIOS RM, ISO 27005)
- [ ] Impact propagation simulation
- [ ] Advanced analytics dashboard
- [ ] Multi-language support
- [ ] Mobile responsive improvements
- [ ] Batch operations for risks
- [ ] Custom risk categories

#### Low Priority
- [ ] SIEM/SOAR integration
- [ ] Email notifications for risk changes
- [ ] Workflow automation
- [ ] AI-powered risk suggestions
- [ ] Collaborative editing features
- [ ] Version control for risk data
- [ ] Integration with project management tools

### Known Issues

- Graph layout resets on data updates (no persistence)
- Limited to ~100 nodes for optimal visualization performance
- No built-in export to common formats (CSV, Excel, PDF)
- Single-user mode only (no concurrent editing)
- Basic error handling (could be more user-friendly)

### Performance Considerations

- Tested with up to 100 risks and 200 influences
- Graph rendering may slow with >150 nodes
- Consider pagination for large datasets
- Neo4j memory allocation may need tuning for large graphs

## Version History

### Version Numbering

- MAJOR version: Incompatible API/schema changes
- MINOR version: Backward-compatible functionality additions
- PATCH version: Backward-compatible bug fixes

### Release Schedule

This is a proof-of-concept project. Release schedule is flexible based on:
- Feature completeness
- Stability testing
- User feedback
- Strategic requirements

## Upgrade Guide

### From Pre-Release to v1.0.0

If you were using a pre-release version:

1. Backup your Neo4j data
2. Stop all services: `docker-compose down`
3. Update repository: `git pull`
4. Update dependencies: `pip install -r requirements.txt --upgrade`
5. Restart services: `docker-compose up -d`
6. Restart application: `streamlit run app.py`

## Migration Notes

### Database Schema Changes

Currently stable at v1.0.0. Future versions will include migration scripts if schema changes are needed.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for details on:
- How to contribute
- Coding standards
- Pull request process
- Development setup

## Support

For issues, questions, or feature requests:
- Open an issue on GitHub
- Check existing documentation
- Review closed issues for solutions

---

**Maintained by**: RIM Development Team  
**License**: MIT  
**Repository**: https://github.com/your-org/RIM_Alpha
