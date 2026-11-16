
import argparse
import re
from collections import Counter

from project.problem import Problem


class RegexProblem(Problem):

    def initialize_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument(
            "--rgx",
            type=int,
            choices=[1, 2, 3, 4, 5]
        )

    def is_chosen_problem(self, args):
        return args.rgx is not None

    def run(self, args):
        if not args.input or not args.output:
            raise ValueError(
                "Az --input és --output megadása kötelező."
            )

        with open(
            args.input,
            "r",
            encoding="utf-8",
            errors="replace"
        ) as f:
            lines = f.readlines()

        log_regex = re.compile(
            r"^(?P<date>\d{2}-\d{2})\s+"
            r"(?P<time>\d{2}:\d{2}:\d{2}\.\d+)\s+"
            r"(?P<pid>\d+)\s+"
            r"(?P<tid>\d+)\s+"
            r"(?P<level>[IDVEFAW])\s+"
            r"(?P<tag>.*?):[ \t]*(?P<message>.*)$"
        )

        logs = []

        for line in lines:
            match = log_regex.match(line)
            if match:
                logs.append(match)

        result = []

        if args.rgx == 1:

            # 1. Október 15-i bejegyzések
            result.append(sum(
                1 for m in logs
                if m.group("date") == "10-15"
            ))

            # 2. Október 15., 10:18:51
            result.append(sum(
                1 for m in logs
                if m.group("date") == "10-15"
                and re.match(
                    r"10:18:51\.",
                    m.group("time")
                )
            ))

            # 3. Az 51. másodpercben történt események
            result.append(sum(
                1 for m in logs
                if re.search(
                    r":51\.",
                    m.group("time")
                )
            ))

            # 4. lowmemorykiller a tagben
            result.append(sum(
                1 for m in logs
                if re.search(
                    r"lowmemorykiller",
                    m.group("tag").strip()
                )
            ))

            # 5. 10:18:51 időpont és PID = 221
            result.append(sum(
                1 for m in logs
                if re.match(
                    r"10:18:51\.",
                    m.group("time")
                )
                and m.group("pid") == "221"
            ))

            # 6. E szintű bejegyzések
            result.append(sum(
                1 for m in logs
                if m.group("level") == "E"
            ))

            # 7. PackageManager a tagben, W szint
            result.append(sum(
                1 for m in logs
                if m.group("level") == "W"
                and re.search(
                    r"PackageManager",
                    m.group("tag").strip()
                )
            ))

            # 8. ExoPlayer a tagben, D szint
            result.append(sum(
                1 for m in logs
                if m.group("level") == "D"
                and re.search(
                    r"ExoPlayer",
                    m.group("tag").strip()
                )
            ))

            # 9. E vagy W szint és Java fájlpozíció
            result.append(sum(
                1 for m in logs
                if m.group("level") in ("E", "W")
                and re.search(
                    r"\.java:\d+",
                    m.group("message")
                )
            ))

            # 10. Thread szöveg az üzenetben
            result.append(sum(
                1 for m in logs
                if re.search(
                    r"Thread",
                    m.group("message")
                )
            ))

        elif args.rgx == 2:

            # Java fájlnevek E szintű bejegyzésekből
            for m in logs:
                if m.group("level") == "E":
                    message = m.group("message")

                    matches = re.finditer(
                        r"([A-Za-z_$][A-Za-z0-9_$]*\.java):\d+",
                        message
                    )

                    for found in matches:
                        result.append(found.group(1))

        elif args.rgx == 3:

            # Egyedi PID-ek előfordulási sorrendben
            seen = set()

            for m in logs:
                pid = m.group("pid")

                if pid not in seen:
                    seen.add(pid)
                    result.append(pid)

        elif args.rgx == 4:

            # Legtöbb E szintű hibával rendelkező PID
            errors = Counter()

            for m in logs:
                if m.group("level") == "E":
                    errors[m.group("pid")] += 1

            if errors:
                pid, count = errors.most_common(1)[0]
                result.append(
                    f"PID={pid} ({count} errors)"
                )

        elif args.rgx == 5:

            # E szintű bejegyzések, ahol PID = TID
            count = sum(
                1 for m in logs
                if m.group("level") == "E"
                and m.group("pid") == m.group("tid")
            )

            result.append(count)

        with open(
            args.output,
            "w",
            encoding="utf-8"
        ) as f:
            for item in result:
                f.write(str(item) + "\n")
