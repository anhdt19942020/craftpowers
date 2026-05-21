---
id: MASS-ASSIGNMENT
severity_max: CRITICAL
applies_to: typescript
---

# Mass Assignment — TypeScript

## Search patterns

- Mongoose: `Model.create(req.body)`, `doc.set(req.body)`
- Sequelize: `Model.create(req.body)`, `instance.update(req.body)`
- TypeORM: `repo.save(req.body)`
- `Object.assign(entity, req.body)`, `{ ...req.body }`

## Fix

Use DTO with Zod/class-validator. Strip extra fields before DB operations.
