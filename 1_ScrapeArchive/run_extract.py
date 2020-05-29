from ExtractArticlesArchive import ExtractArchive


tags = ["web-development", "software-engineering",
        "programming", "Data-science"]

years = [2018, 2019]
dropbox_token = "<INSERT DROPBOX TOKEN HERE>"
obj = ExtractArchive(tags, years, dropbox_token)
obj.run()
