from prisma import Prisma

prisma = Prisma(
    use_dotenv=True, 
    auto_register=True
)