import json
from pathlib import Path
import unittest
from urllib.parse import parse_qs, urlsplit
import re

ROOT = Path(__file__).resolve().parents[1]
SERVICE = 'serp'
ALIAS = '${ACEDATACLOUD_SERP_TOKEN}'
GUIDE_TOOL = 'serp_list_search_types'


class ExtensionTests(unittest.TestCase):
    def test_pinned_server_and_scoped_tools(self):
        manifest = json.loads((ROOT / 'qwen-extension.json').read_text())
        self.assertEqual(list(manifest['mcpServers']), [SERVICE])
        server = manifest['mcpServers'][SERVICE]
        self.assertEqual(server['command'], 'uvx')
        self.assertRegex(server['args'][0], r'^mcp-[a-z-]+==[0-9]+(?:\.[0-9]+)+$')
        self.assertEqual(server['env'], {'ACEDATACLOUD_API_TOKEN': ALIAS})
        self.assertEqual(len(server['includeTools']), len(set(server['includeTools'])))
        self.assertTrue(all(tool.startswith(SERVICE + '_') for tool in server['includeTools']))
        self.assertIn(GUIDE_TOOL, server['includeTools'])
        self.assertIn(GUIDE_TOOL, (ROOT / 'commands/first-use.md').read_text())

    def test_artwork_and_referrals(self):
        self.assertTrue((ROOT / 'assets/icon.png').read_bytes().startswith(b'\x89PNG'))
        for path, source in [('README.md', 'github'), ('QWEN.md','qwen-code')]:
            links = re.findall(r'\]\((https://platform\.acedata\.cloud/[^)]+)\)', (ROOT / path).read_text())
            self.assertTrue(links)
            for link in links:
                self.assertEqual(parse_qs(urlsplit(link).query), {'utm_source': [source], 'utm_medium': ['referral'], 'utm_campaign': ['evergreen']})
