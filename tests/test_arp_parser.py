import unittest
from app import parse_arp_output


class ArpParserTests(unittest.TestCase):
    def test_parses_ip_interface_and_raw_line(self):
        sample_output = """
        ? (192.168.1.1) at 00:11:22:33:44:55 [ether] on eth0
        ? (192.168.1.10) at AA:BB:CC:DD:EE:FF [ether] on wlan0
        """

        parsed = parse_arp_output(sample_output)

        self.assertEqual(len(parsed), 2)
        self.assertEqual(parsed[0]["ip_address"], "192.168.1.1")
        self.assertEqual(parsed[0]["mac"], "00-11-22-33-44-55")
        self.assertEqual(parsed[0]["interface"], "eth0")
        self.assertIn("192.168.1.1", parsed[0]["raw_line"])


if __name__ == "__main__":
    unittest.main()
