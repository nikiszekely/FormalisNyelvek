
from project.problem import Problem


class Minimize(Problem):

    def initialize_parser(self, parser):
        parser.add_argument(
            "--mini",
            action="store_true",
            help="Veges automata minimalizalasa"
        )

    def is_chosen_problem(self, args):
        return args.mini

    def run(self, args):
        if not args.input:
            raise ValueError("Add meg a bemeneti fajlt a --input kapcsoloval!")

        if not args.output:
            raise ValueError("Add meg a kimeneti fajlt a --output kapcsoloval!")

        self.minimalizalas(args.input, args.output)

    def minimalizalas(self, input_fajl, output_fajl):
        # bemeneti fajl beolvasasa
        try:
            with open(input_fajl, "r", encoding="utf-8") as fajl:
                sorok = fajl.read().splitlines()
        except OSError as hiba:
            raise ValueError(f"Nem sikerult megnyitni a bemeneti fajlt: {hiba}")

        if len(sorok) < 4:
            raise ValueError("A bemeneti fajl legalabb 4 sort tartalmazzon!")

        # felbontas
        allapotok = sorok[0].split()
        abc = sorted(sorok[1].split())
        kezdo = sorok[2].strip()
        vegallapotok = set(sorok[3].split())

        if not allapotok:
            raise ValueError("Nincs megadva egyetlen allapot sem!")

        if len(allapotok) != len(set(allapotok)):
            raise ValueError("Az allapotok kozott ismetlodes van!")

        if len(abc) != len(set(abc)):
            raise ValueError("Az abeceben ismetlodo jel van!")

        allapot_halmaz = set(allapotok)
        abc_halmaz = set(abc)

        if kezdo not in allapot_halmaz:
            raise ValueError(f"Ismeretlen kezdoallapot: {kezdo}")

        for allapot in vegallapotok:
            if allapot not in allapot_halmaz:
                raise ValueError(f"Ismeretlen vegallapot: {allapot}")

        # atmenetek beolvasasa
        atmenetek = {}

        for sorszam, sor in enumerate(sorok[4:], start=5):
            elemek = sor.split()

            if not elemek:
                continue

            if len(elemek) != 3:
                raise ValueError(f"Hibas atmenet a(z) {sorszam}. sorban!")

            forras, jel, cel = elemek

            if forras not in allapot_halmaz:
                raise ValueError(
                    f"Ismeretlen forrasallapot a(z) {sorszam}. sorban: {forras}"
                )

            if cel not in allapot_halmaz:
                raise ValueError(
                    f"Ismeretlen celallapot a(z) {sorszam}. sorban: {cel}"
                )

            if jel not in abc_halmaz:
                raise ValueError(
                    f"Ismeretlen bemeneti jel a(z) {sorszam}. sorban: {jel}"
                )

            if (forras, jel) in atmenetek:
                if atmenetek[(forras, jel)] != cel:
                    raise ValueError("Az automata nem determinisztikus!")

            atmenetek[(forras, jel)] = cel

        # kezdeti csoportok
        nem_vegallapotok = allapot_halmaz - vegallapotok

        csoportok = []

        if nem_vegallapotok:
            csoportok.append(nem_vegallapotok)

        if vegallapotok:
            csoportok.append(vegallapotok)

        # csoportok finomitasa
        while True:
            uj_csoportok = []

            for csoport in csoportok:
                alcsoportok = {}

                for allapot in sorted(csoport):
                    alairas = []

                    for jel in abc:
                        cel = atmenetek.get((allapot, jel))

                        if cel is None:
                            alairas.append(-1)
                        else:
                            for i, masik_csoport in enumerate(csoportok):
                                if cel in masik_csoport:
                                    alairas.append(i)
                                    break

                    alairas = tuple(alairas)
                    alcsoportok.setdefault(alairas, set()).add(allapot)

                uj_csoportok.extend(alcsoportok.values())

            if len(uj_csoportok) == len(csoportok):
                csoportok = uj_csoportok
                break

            csoportok = uj_csoportok

        # uj allapotnevek meghatarozasa
        def sorszam(allapot):
            return int(allapot[1:])

        uj_nevek = {}

        for csoport in csoportok:
            legkisebb = min(csoport, key=sorszam)
            uj_nev = "s" + legkisebb[1:]

            for allapot in csoport:
                uj_nevek[allapot] = uj_nev

        # uj allapotok
        uj_allapotok = sorted(
            set(uj_nevek.values()),
            key=sorszam
        )

        uj_kezdo = uj_nevek[kezdo]

        uj_vegallapotok = sorted(
            {uj_nevek[allapot] for allapot in vegallapotok},
            key=sorszam
        )

        # uj atmenetek
        uj_atmenetek = set()

        for (forras, jel), cel in atmenetek.items():
            uj_forras = uj_nevek[forras]
            uj_cel = uj_nevek[cel]

            uj_atmenetek.add((uj_forras, jel, uj_cel))

        # atmenetek rendezese
        uj_atmenetek = sorted(
            uj_atmenetek,
            key=lambda atmenet: (
                sorszam(atmenet[0]),
                atmenet[1],
                sorszam(atmenet[2])
            )
        )

        # eredmeny kiirasa
        try:
            with open(output_fajl, "w", encoding="utf-8") as fajl:
                fajl.write(" ".join(uj_allapotok) + "\n")
                fajl.write(" ".join(abc) + "\n")
                fajl.write(uj_kezdo + "\n")
                fajl.write(" ".join(uj_vegallapotok) + "\n")

                for forras, jel, cel in uj_atmenetek:
                    fajl.write(f"{forras} {jel} {cel}\n")

        except OSError as hiba:
            raise ValueError(f"Nem sikerult kiirni a kimeneti fajlt: {hiba}")

        print(f"A minimalizalas sikeres: {output_fajl}")
