from .maroon import maroon

async def setup(bot):
    await bot.add_cog(maroon(bot))