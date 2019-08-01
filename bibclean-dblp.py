#!/usr/bin/env python3

import biblib.bib
import argparse
import sys
import requests
import urllib.parse
from pprint import pprint
import re

def main():
    arg_parser = argparse.ArgumentParser(
        description='Flatten macros, combine, and pretty-print .bib database(s)')
    arg_parser.add_argument('bib', nargs='+', help='.bib file(s) to process',
                            type=open)
    arg_parser.add_argument('--min-crossrefs', type=int,
                            help='minimum number of cross-referencing entries'
                            ' required to expand a crossref; if omitted, no'
                            ' expansion occurs', default=None)
    args = arg_parser.parse_args()

    try:
        # Load databases
        db = biblib.bib.Parser().parse(args.bib, log_fp=sys.stderr).get_entries()

        # Optionally resolve cross-references
        if args.min_crossrefs is not None:
            db = biblib.bib.resolve_crossrefs(
                db, min_crossrefs=args.min_crossrefs)

    except biblib.messages.InputError:
        sys.exit(1)

    # Pretty-print entries
    queries = []
    for ent in db.values():
        try:
          title = ent["title"]
          year = ent["year"]
          oquery = year +" "+ title +" "+ " ".join(i.last for i in ent.authors())
          oquery = re.sub("[^ ]\\\\.", lambda x: x[0][0], oquery)
          oquery = re.sub("\\\\[^{]+?[ {]", lambda x: "", oquery)
          oquery = oquery.replace("{", "").replace("}", "")
          query = oquery.replace(" ", "+")
          query = urllib.parse.quote(query)
          query = query.replace("%2B", "+")
          queries.append((ent, oquery, query))
        except:
          pass

    mode = "bib"
    if mode=="bib":
        #queries = sorted(queries, key=lambda x: x[1])
        for i, (ent, oquery, query) in enumerate(queries):
            print()
            resp = requests.get("https://dblp.org/search/publ/api?format=bib&q=" + query).text
            if resp:
                respbib = biblib.bib.Parser().parse(resp, log_fp=sys.stderr).get_entries()
                if len(respbib) == 1:
                    print("% OK ", oquery)
                    bibl = respbib[list(respbib)[0]]
                    bibl.key = ent.key
                    print(bibl.to_bib(wrap_width=120))
                    continue
            print("% BAD", oquery)
            print(ent.to_bib(wrap_width=120))

    else:
        fails = []
        succs = {}
        for i, (ent, oquery, query) in enumerate(queries):
            print(i)
            print("=", oquery)
            resp = requests.get("https://dblp.org/search/publ/api?format=json&q=" + query).json()

            if resp and "hit" in resp["result"]["hits"]:
                for hit in resp["result"]["hits"]["hit"]:
                    try:
                        venue = hit["info"].get("venue", hit["info"].get("booktitle", "-"))
                        succs[venue] = succs.get(venue, 0) + 1
                        print("*", hit["info"]["year"] +" "+
                              hit["info"]["authors"]["author"][0].split(" ")[-1] +". "+
                              hit["info"]["title"] +" "+
                              venue)
                    except:
                        pprint(hit["info"])
                        pass
            else:
                fails.append( oquery )
            print()
            print()

        pprint(fails)
        pprint(succs)
        print(len(fails))


if __name__ == '__main__':
    main()
