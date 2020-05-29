from test_lda_data import feature_matrix, userProfile
from DocRecommendor import DocRecommender


obj = DocRecommender(userProfile , feature_matrix)
email_data= obj.genRecommendations()

print(email_data)