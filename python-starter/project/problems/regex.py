
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

        # Logfájl beolvasása
        with open(
            args.input,
            "r",
            encoding="utf-8",
            errors="replace"
        ) as f:
            lines = f.readlines()

        # Logbejegyzések feldolgozása regex segítségével
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
                if re.fullmatch(
                    r"10-15",
                    m.group("date")
                )
            ))

            # 2. Október 15., 10:18:51
            result.append(sum(
                1 for m in logs
                if re.fullmatch(
                    r"10-15",
                    m.group("date")
                )
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

            # 4. lowmemorykiller tag
            result.append(sum(
                1 for m in logs
                if re.fullmatch(
                    r"lowmemorykiller",
                    m.group("tag")
                )
            ))

            # 5. 10:18:51 időpont és PID = 221
            result.append(sum(
                1 for m in logs
                if re.match(
                    r"10:18:51\.",
                    m.group("time")
                )
                and re.fullmatch(
                    r"221",
                    m.group("pid")
                )
            ))

            # 6. E szintű bejegyzések
            result.append(sum(
                1 for m in logs
                if re.fullmatch(
                    r"E",
                    m.group("level")
                )
            ))

            # 7. PackageManager tag és W szint
            result.append(sum(
                1 for m in logs
                if re.fullmatch(
                    r"W",
                    m.group("level")
                )
                and re.fullmatch(
                    r"PackageManager",
                    m.group("tag")
                )
            ))

            # 8. ExoPlayer tag és D szint
            result.append(sum(
                1 for m in logs
                if re.fullmatch(
                    r"D",
                    m.group("level")
                )
                and re.fullmatch(
                    r"ExoPlayer",
                    m.group("tag")
                )
            ))

            # 9. E vagy W szint és Java fájlpozíció
            result.append(sum(
                1 for m in logs
                if re.fullmatch(
                    r"[EW]",
                    m.group("level")
                )
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
            # Az ismétlődő fájlnevek is megmaradnak
            for m in logs:
                if re.fullmatch(r"E", m.group("level")):

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
                if re.fullmatch(
                    r"E",
                    m.group("level")
                ):
                    pid = m.group("pid")
                    errors[pid] += 1

            if errors:
                pid, count = errors.most_common(1)[0]

                result.append(
                    f"PID={pid} ({count} errors)."
                )

        elif args.rgx == 5:

            # E szintű bejegyzések, ahol PID = TID
            count = sum(
                1 for m in logs
                if re.fullmatch(
                    r"E",
                    m.group("level")
                )
                and m.group("pid") == m.group("tid")
            )

            result.append(count)

        # Eredmények kiírása
        with open(
            args.output,
            "w",
            encoding="utf-8"
        ) as f:
            for item in result:
                f.write(str(item) + "\n")
