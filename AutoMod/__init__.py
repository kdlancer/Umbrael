from .autoMod import autoMod

async def setup(bot):
    await bot.add_cog(autoMod(bot))