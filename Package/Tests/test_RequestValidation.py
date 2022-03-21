from  Package.DataStructures.requestBody import *
import unittest, json, tqdm

class TestRequestValidation(unittest.TestCase):
    """class for testing the importing and validation of the TCP Request"""

    def import_examples(self, path="D:\HZDR\HZDR_VISU_TOOL\Package\Tests\Test_Requests.json") ->dict:
        """function responsable for importing the test jsons from a file"""
        with open(path, "r") as test_file:
            test = json.load(test_file)
        return test

    def goahead(self, data)->Request:
        """function responsible for parsing the json file to a Request Model class"""
        channels: Dict[str, ChannelData] = dict(
            (id_, ChannelData(**channel)) for id_, channel in data.get("Body").get("data").get("channels").items())

        return Request(Status=RequestStatus(**data.get("Status")),
                Body=RequestBody(metaData=RequestMetaData(**data.get("Body").get("metaData")),
                                 data=RequestData(dataSize=data.get("Body").get("data").get("dataSize"),
                                                  timesteps=data.get("Body").get("data").get("timesteps"),
                                                  channels=channels)))

    def test_correct_format(self) -> None:
        data: dict = self.import_examples().get("correct")
        manual_obj = self.goahead(data)
        auto_obj = Request.parse_obj(data)
        print(manual_obj)
        print(auto_obj)
        self.assertEqual(manual_obj, auto_obj)

    def test_empty_channel_data(self)->None:
        data:dict= self.import_examples()
        # print(data.get("wrongDatasize"))
        # print(Request.parse_obj(data.get("wrongDatasize")))
        self.assertRaises(EmptyRequestException, lambda: Request.parse_obj(data.get("noChannelData")))
        # self.assertRaises(EmptyRequestException, lambda: self.goahead(data.get("noChannelData")))
    def test_mishaped_data(self)->None:
        data:dict = self.import_examples()
        self.assertRaises(DataShapeException, lambda: self.goahead(data.get("wrongDatasize")))
    def test_mishaped_data2(self)->None:
        data:dict = self.import_examples()
        self.assertRaises(DataShapeException, lambda: self.goahead(data.get("MissingElementInOneArray")))
    def test_unordered_timeSerie(self)->None:
        data:dict = self.import_examples()
        self.assertRaises(UnorderedTimeSerieException, lambda: self.goahead(data.get("UnorderedTimeSerie")))


if __name__ == "__main__":
    unittest.main()