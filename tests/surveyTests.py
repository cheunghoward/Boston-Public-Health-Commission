from application import application as pli, mail
from urllib import quote_plus
from testlib import *
from pli import validate_login, encode_uid, decode_uid, is_confirmed_uid, send_confirmation_email
from datetime import date
import unittest


class RetrieveSurveyTest(unittest.TestCase):
    def setUp(self):
        pli.config['db'] = mocked_surveys()

    def test_retreive_valid_survey(self):
        test_survey1 = retrieve_survey(1111)
        self.assertEqual(len(test_survey1["questions"]), 2)
        self.assertEqual(test_survey1["questions"][0]["ask"], "When did you last....")
        self.assertEqual(len(test_survey1["questions"][0]["answers"]), 4)

    #invalid survey_id
    def test_retreive_invalid_survey(self):
        try:
            invalid_survey = retrieve_survey(1253246622)
        except ValueError as e:
            self.assertEqual(str(e), "Invalid survey id")


class SubmitResponseTest(unittest.TestCase):
    def setUp(self):
        pli.config['db'] = mocked_surveys()

    def test_submit_valid_response(self):
        survey_id = 3333
        ans_ids = [1, 2, 3, 4]
        date_taken = date()

        resp = dict(survey_id=survey_id, ans_ids=ans_ids, taken=date_taken)

        #Returns the mongo _id of the submitted response
        self.assertTrue(submit_response(resp) > 0)

    #invalid id
    def test_submit_invalid_response1(self):
        survey_id = 32542352465
        ans_ids = [1, 2, 3, 4]
        date_taken = date()

        resp = dict(survey_id=survey_id, ans_ids=ans_ids, taken=date_taken)

        #Returns the mongo _id of the submitted response
        try:
            submit_response(resp)
        except ValueError as e:
            self.assertEqual(str(e), "No survey {sid} exists".format(sid=survey_id))

    #too many questions
    def test_submit_invalid_response2(self):
        survey_id = 1111
        ans_ids = [1, 2, 3, 4]
        date_taken = date()

        resp = dict(survey_id=survey_id, ans_ids=ans_ids, taken=date_taken)

        try:
            submit_response(resp)
        except ValueError as e:
            self.assertEqual(str(e), "Invalid number of questions for {sid}. \
            Given: {answers}. Expected: 2".format(sid=survey_id, answers=len(ans_ids)))

    #Not enough questions
    def test_submit_invalid_response3(self):
        survey_id = 3333
        ans_ids = [1, 2, 3]
        date_taken = date()

        resp = dict(survey_id=survey_id, ans_ids=ans_ids, taken=date_taken)

        try:
            submit_response(resp)
        except ValueError as e:
            self.assertEqual(str(e), "Invalid number of questions for {sid}. \
            Given: {answers}. Expected: 4".format(sid=survey_id, answers=len(ans_ids)))

    #invalid ans_id for a questoin
    def test_submit_invalid_response4(self):
        survey_id = 3333
        ans_ids = [1, 2, 3, 7]
        date_taken = date()

        resp = dict(survey_id=survey_id, ans_ids=ans_ids, taken=date_taken)

        #Returns the mongo _id of the submitted response
        try:
            submit_response(resp)
        except ValueError as e:
            self.assertEqual(str(e), "Invalid answer id for question in ans_ids")


class CreateQuestionTest(unittest.TestCase):
    def setUp(self):
        pli.config['db'] = mocked_surveys()

    def test_create_question(self):
        ask = "Do you like me?"
        ans1 = dict(ans_id=1, answer="Yes")
        ans2 = dict(ans_id=2, answer="No")

        q_obj = dict(question=ask,answers=[ans1, ans2])

        #Returns id for newly created question
        self.assertTrue(create_question(q_obj) > 0)


class CreateSurveyTest(unittest.TestCase):
    def setUp(self):
        pli.config['db'] = mocked_surveys()

    def test_create_valid_survey(self):
        qids = [0004, 0003, 0002, 0001]

        #Returns id for newly created question
        self.assertTrue(create_survey(qids) > 0)

    #invalid question id
    def test_create_valid_survey(self):
        qids = [0004, 0003, 0002, 00011]

        try:
            create_survey(qids)
        except ValueError as e:
            self.assertEqual(str(e), "Invalid question id (does not exist) for new survey")
