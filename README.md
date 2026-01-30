# Minecraft Mod Sorter

Automatically sort Minecraft mods into client-only, server-only, and both using the Modrinth API.

## Requirements

- Python 3.6+
- Internet connection

## How It Works

The tool scans your mods folder and uses Modrinth's API to determine where each mod should be installed:

- **client-only/** - Install only on client (shaders, minimaps, performance mods)
- **server-only/** - Install only on server (management tools, anti-cheat)
- **both/** - Install on both client and server (content mods, tech mods)
- **unknown/** - Not found on Modrinth (check manually)

## Output

Creates a `sorted_mods` folder with your mods organized into the categories above. Original files are unchanged.

## Notes

- Uses SHA1/SHA512 hashes for identification
- Adds delays between API calls to be respectful
- Mods not on Modrinth go in "unknown" folder

## License

MIT License - see [LICENSE](LICENSE) file.

## Credits

Uses the [Modrinth API](https://docs.modrinth.com/)
