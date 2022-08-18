import os
import math
import json
import pke
import numpy as np
from rank_bm25 import BM25Okapi
import pickle
from nltk.tokenize import TextTilingTokenizer

from documents.models import Document, SuspiciousDocument, GivenPlagiarismCase
from django.core.management.base import BaseCommand


def further_filter_candidates(extractor):
    for k in list(extractor.candidates):

        # get the candidate
        v = extractor.candidates[k]

        # filter candidates starting/ending with a stopword or containing
        # a first/last word with less than 3 characters
        if (
            v.surface_forms[0][0].lower() in extractor.stoplist
            or v.surface_forms[0][-1].lower() in extractor.stoplist
            or not v.surface_forms[0][0].isalnum()
            or len(v.surface_forms[0][0]) < 3
            or len(v.surface_forms[0][-1]) < 3
        ):
            del extractor.candidates[k]


class Command(BaseCommand):
    help = "Extract keywords using rake"

    def handle(self, *args, **options):
        curpath = os.path.dirname(__file__)
        dataset_path = "../../../../dataset-preprocessed/source-document"

        english_doc_nums = Document.objects.filter(language="en").values_list(
            "doc_num", flat=True
        )

        # create inverted index
        # corpus = []
        # for file_number in english_doc_nums:
        #     part_number = math.ceil(file_number / 500)
        #
        #     with open(
        #         os.path.join(
        #             curpath,
        #             dataset_path,
        #             f"part{part_number}",
        #             f"source-document{str(file_number).rjust(5, '0')}.txt",
        #         ),
        #         "r",
        #     ) as f:
        #         corpus.append(f.read().split(" "))
        #
        # print("done creating corpus")
        # bm25 = BM25Okapi(corpus)
        #
        # with open(
        #     os.path.join(curpath, dataset_path, "../" "bm25.pickle"), "wb"
        # ) as model_file:
        #     pickle.dump(bm25, model_file)

        # get tfidf keywords
        # with open(
        #     os.path.join(curpath, dataset_path, "../tfidf-model.pickle"), "rb"
        # ) as model_file:
        #     tfidf_vectorizer = pickle.load(model_file)
        #     feature_array = tfidf_vectorizer.get_feature_names_out()
        #
        # sus_filenum = 9992
        # part_number = math.ceil(sus_filenum / 500)
        # suspicious_vector = tfidf_vectorizer.transform(
        #     [
        #         os.path.join(
        #             curpath,
        #             dataset_path,
        #             f"../suspicious-document/part{part_number}",
        #             f"suspicious-document{str(sus_filenum).rjust(5, '0')}.txt",
        #         )
        #     ]
        # )
        #
        # tfidf_sorting = np.argsort(suspicious_vector.toarray()).flatten()[::-1]
        # query = feature_array[tfidf_sorting][:50].tolist()

        # suspicious doc nums
        # sus_doc_nums = SuspiciousDocument.objects.all().values_list(
        #     "doc_num", flat=True
        # )
        # with open(
        #     os.path.join(curpath, dataset_path, "../suspicious-doc-nums.json"), "w"
        # ) as model_file:
        #     json.dump({"suspiciousDocNums": list(sus_doc_nums)}, model_file)

        with open(
            os.path.join(curpath, dataset_path, "../bm25.pickle"), "rb"
        ) as model_file:
            bm25 = pickle.load(model_file)

        sus_doc = SuspiciousDocument.objects.get(doc_num=947)
        raw_text = sus_doc.raw_text

        extractor = pke.unsupervised.YAKE()
        ttt = TextTilingTokenizer(w=50, k=5)
        segments = ttt.tokenize(raw_text)
        print(len(segments))
        print("finish segmenting")

        queries = []
        for segment in segments:
            text_length = len(segment)
            for i in range(0, math.ceil(text_length / 1000000)):
                extractor.load_document(
                    input=segment[1000000 * i : 1000000 * (i + 1)],
                    language="en",
                )
                extractor.ngram_selection(n=1)
                # extractor.candidate_filtering(pos_blacklist=["VERB", "NUM"])
                further_filter_candidates(extractor)
                extractor.candidate_weighting()

                query = [
                    keyword for keyword, _ in extractor.get_n_best(n=10, stemming=False)
                ]
                queries.append(query)
        print(queries)

        print("Finish formating query")

        all_candidates = []
        for query in queries:
            # query = json.loads(sus_doc.keywords)
            doc_scores = bm25.get_scores(query)
            top_indices = np.argsort(doc_scores)[::-1]

            # candidates = []
            for index in top_indices[0:10]:
                all_candidates.append(english_doc_nums[int(index)])
            # all_candidates.append(candidates)

        print("Finished getting candidates")
        all_candidates = list(set(all_candidates))
        print(len(all_candidates))

        given_sources = sus_doc.given_plagiarised_source_document()
        for given_source in given_sources:
            print(given_source in all_candidates)
