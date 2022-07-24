import os
import pickle
import fasttext
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from django.http import JsonResponse
from .models import Document, SuspiciousDocument


def merge_sentences(arr, window=2):
    if len(arr) < 2:
        return [arr.copy()], [[]]

    start = 0
    end = 1
    merge_arr = []
    merge_at = []
    while end < len(arr):
        if arr[end] - arr[end - 1] <= window and end != len(arr) - 1:
            end = end + 1
            continue

        if end == len(arr) - 1:
            if arr[end] - arr[end - 1] <= window:
                merge_at.append([start, end + 1])
                merge_arr.append(arr[start : end + 1])
            else:
                merge_at.append([start, end])
                merge_arr.append(arr[start:end])
                merge_at.append([end, end + 1])
                merge_arr.append(arr[end : end + 1])
        else:
            merge_at.append([start, end])
            merge_arr.append(arr[start:end])
            start = end

        end = end + 1
    return merge_arr, merge_at


def merge_suspicious_sentences(arr, window=2):
    if len(arr) < 2:
        return [arr.copy()], [[]]

    start = 0
    end = 1
    merge_arr = []
    merge_at = []
    while end < len(arr):
        if (
            arr[end]["number"] - arr[end - 1]["number"] <= window
            and end != len(arr) - 1
        ):
            end = end + 1
            continue

        if end == len(arr) - 1:
            if arr[end]["number"] - arr[end - 1]["number"] <= window:
                merge_at.append([start, end + 1])
                merge_arr.append(arr[start : end + 1])
            else:
                merge_at.append([start, end])
                merge_arr.append(arr[start:end])
                merge_at.append([end, end + 1])
                merge_arr.append(arr[end : end + 1])
        else:
            merge_at.append([start, end])
            merge_arr.append(arr[start:end])
            start = end

        end = end + 1
    return merge_arr, merge_at


# Create your views here.
def detail_analysis(request, filenum):
    """Detail analysis of a suspicious document"""
    response = {}
    if request.method == "GET":
        curpath = os.path.dirname(__file__)
        # model = fasttext.load_model(os.path.join(curpath, "wiki.en.bin"))
        #
        suspicious_document = SuspiciousDocument.objects.get(doc_num=filenum)
        # suspicious_raw_sentences = [
        #     sentence.raw_text for sentence in suspicious_document.sentences.all()
        # ]
        # suspicious_sentences = [
        #     sentence.preprocessed_text
        #     for sentence in suspicious_document.sentences.all()
        # ]
        # suspicious_sent_vectors = []
        # for sentence in suspicious_sentences:
        #     sent_vector = np.zeros(shape=(300,))
        #     words = sentence.split(",")
        #     sentence_length = len(words)
        #
        #     for word in words:
        #         sent_vector = np.add(sent_vector, model.get_word_vector(word))
        #
        #     suspicious_sent_vectors.append(sent_vector / sentence_length)

        source_document = Document.objects.get(doc_num=5693)
        # source_raw_sentences = [
        #     sentence.raw_text for sentence in source_document.sentences.all()
        # ]
        # source_sentences = [
        #     sentence.preprocessed_text for sentence in source_document.sentences.all()
        # ]
        # source_sent_vectors = []
        # for sentence in source_sentences:
        #     sent_vector = np.zeros(shape=(300,))
        #     words = sentence.split(",")
        #     sentence_length = len(words)
        #
        #     for word in words:
        #         sent_vector = np.add(sent_vector, model.get_word_vector(word))
        #
        #     source_sent_vectors.append(sent_vector / sentence_length)
        #
        # cosine_similarities = cosine_similarity(
        #     suspicious_sent_vectors, source_sent_vectors
        # )
        # with open(os.path.join(curpath, "cosine_similarities.pickle"), "wb") as file:
        #     pickle.dump(cosine_similarities, file)

        with open(os.path.join(curpath, "cosine_similarities.pickle"), "rb") as file:
            cosine_similarities = pickle.load(file)

        top_n = 5
        detected_suspicious_sentences = []
        detected_source_sentences = []
        for idx, similarity in enumerate(cosine_similarities):
            top_indices = np.argsort(similarity)[::-1][:top_n]
            for index in top_indices:
                if similarity[index] > 0.95:
                    detected_suspicious_sentences.append(idx)
                    s = {"number": int(index)}
                    s["score"] = similarity[index]
                    detected_source_sentences.append(s)

        merged_suspicious_sentences, merge_at = merge_sentences(
            detected_suspicious_sentences
        )
        merged_source_sentences = []
        for idxs in merge_at:
            merged_source_sentences.append(detected_source_sentences[idxs[0] : idxs[1]])

        merged_merged = []
        for sentence in merged_source_sentences:
            s = sorted(sentence, key=lambda x: x["number"])
            merg, _ = merge_suspicious_sentences(s)
            merged_merged.append(merg)

        response = suspicious_document.serialize()
        response["potential-case"] = []
        for idx, merged in enumerate(merged_suspicious_sentences):
            sentences = suspicious_document.sentences.filter(
                number__gte=min(merged), number__lte=max(merged)
            )
            concanated_sentence = ""
            for sentence in sentences:
                concanated_sentence += f" {sentence.raw_text}"
            response["potential-case"].append({"sentence": concanated_sentence})

        for idx, merged in enumerate(merged_merged):
            response["potential-case"][idx]["source"] = []
            for mm in merged:
                sentences = source_document.sentences.filter(
                    number__gte=min(mm, key=lambda x: x["number"])["number"],
                    number__lte=max(mm, key=lambda x: x["number"])["number"],
                )
                r = {}
                r["filenum"] = 5693
                concanated_sentence = ""
                for sentence in sentences:
                    concanated_sentence += f" {sentence.raw_text}"
                r["sentence"] = concanated_sentence

                total_score = 0
                for m in mm:
                    total_score = total_score + m["score"]
                average_score = total_score / len(mm)
                r["average-score"] = average_score

                response["potential-case"][idx]["source"].append(r)

        # response = {
        #     "suspicious_sentences": merged_suspicious_sentences,
        #     "source_sentences": merged_merged,
        # }

    return JsonResponse(response)
