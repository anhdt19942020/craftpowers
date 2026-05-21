---
id: SQL-INJECTION
severity_max: CRITICAL
applies_to: typescript
---

# SQL Injection — TypeScript

Many ORMs with specific dangerous patterns.

## Search patterns

- Sequelize: `sequelize.query("SELECT ... " + input)`, `Sequelize.literal(input)`
- TypeORM: `repo.query("SELECT ... " + input)`, `createQueryBuilder().where("id = " + input)`
- Prisma: `prisma.$queryRawUnsafe("SELECT ... " + input)`
- Knex: `knex.raw("SELECT ... " + input)`
- Mongoose: `Model.find({ $where: "this.name == '" + input + "'" })`

Safe: ORM query builders with parameterized inputs.

## Fix

Use ORM query builder or parameterized raw queries. Prisma: `prisma.$queryRaw` with tagged template.
