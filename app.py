from lfqa_utils import *
from flask import Flask, request, jsonify
import json
import time

# flask development server
app = Flask(__name__)

# random initialization
def set_seed(seed):
  torch.manual_seed(seed)
  if torch.cuda.is_available():
    torch.cuda.manual_seed_all(seed)

set_seed(42)

# cuda cpu or gpu if available and over 4GB
computeDevice = torch.device("cuda" if torch.cuda.is_available()  else "cpu")
if computeDevice.type == 'cuda':
    if not( torch.cuda.get_device_properties("cuda").total_memory > 4231725056):
        computeDevice = torch.device("cpu")
print ("device ",computeDevice)

# clear cuda memory
torch.cuda.empty_cache()

# Service set up
# try:
#     print("Trying to connect to dockerized Elasticsearch...")
#     es_client = Elasticsearch([{'host': 'es01', 'port': '9200'}])
#     time.sleep(5) 
#     print( es_client.indices.get_alias("*") )
#     print("...done")
# except:
#     print("Dockerized Elasticsearch not available, trying localhost port 9200...")
#     es_client = Elasticsearch([{'host': 'localhost', 'port': '9200'}])
#     print( es_client.indices.get_alias("*") )
#     print("...done")

# robustly connect to host or docker elasticsearch
es_client = Elasticsearch(["localhost","es01"])

# bart for seq2seq answer generation
qa_s2s_tokenizer = AutoTokenizer.from_pretrained('yjernite/bart_eli5')
qa_s2s_model = AutoModelForSeq2SeqLM.from_pretrained('yjernite/bart_eli5').to(computeDevice) #'cuda:0')
_ = qa_s2s_model.eval()


#=======================================================================================
# Service functions

# Index a book using JSON snippets of book
# Since this requires POSTing a whole book, it may exceed POST maximum size
def createIndex(snippets,indexName='ap_snippets_100w'):

        if not es_client.indices.exists(indexName):
            make_es_index_snippets_textbook(es_client, snippets, index_name=indexName)
            return "Indexed " + indexName
        else:
            return indexName + " already exists, aborting"

def getAllIndices():
    indices = es_client.indices.get_alias("*")
    return indices

def getDocuments(query,indexName='ap_snippets_100w'):
    question = query
    doc, res_list = query_es_index_textbook(question, es_client, index_name=indexName)
    df = pd.DataFrame({
    'Article': ['---'] + [res['article_title'] for res in res_list],
    'Sections': ['---'] + [res['section_title'] if res['section_title'].strip() != '' else res['article_title'] for res in res_list],
    'Text': ['--- ' + question] + [res['passage_text'] for res in res_list], 
    })
    df.style.set_properties(**{'text-align': 'left'})
    return df.to_dict('records')

def getAnswer(question,indexName='ap_snippets_100w'):
    doc, res_list = query_es_index_textbook(question, es_client, index_name=indexName)
    question_doc = "question: {} context: {}".format(question, doc)
    # save docs results for logging
    df = pd.DataFrame({
    'Article': ['---'] + [res['article_title'] for res in res_list],
    'Sections': ['---'] + [res['section_title'] if res['section_title'].strip() != '' else res['article_title'] for res in res_list],
    'Text': ['--- ' + question] + [res['passage_text'] for res in res_list], 
    })
    df.style.set_properties(**{'text-align': 'left'})
    result = {}
    result['documents'] = df.to_dict('records')
    # generate an answer with beam search
    answer = qa_s2s_generate(
        question_doc, qa_s2s_model, qa_s2s_tokenizer,
        num_answers=1,
        num_beams=8,
        min_len=64,
        max_len=256,
        max_input_length=1024,
        # device="cuda:0"
        device = computeDevice
    )[0]
    result['answer'] = answer
    return result

#=======================================================================================
# Instructions/help
@app.route('/')
def api_help():
    return 'API for longform-qa-service, see https://github.com/aolney/longform-qa-service'

# getAnswer(question,indexName)
@app.route('/api/getAnswer', methods=['GET', 'POST'])
def api_getAnswer():
    content = request.get_json()
    result = getAnswer( content['question'], content.get('indexName','ap_snippets_100w') )
    return jsonify(result)

# createIndex(fileName,indexName)
@app.route('/api/createIndex', methods=['GET', 'POST'])
def api_createIndex():
    content = request.get_json()
    result = createIndex( content['snippets'], content.get('indexName','ap_snippets_100w') )
    return jsonify( result  )

    getAllIndices

# getAllIndices()
@app.route('/api/getAllIndices', methods=['GET', 'POST'])
def api_getAllIndices():
    result = getAllIndices( )
    return jsonify( result  )

# getDocuments(query,indexName)
@app.route('/api/getDocuments', methods=['GET', 'POST'])
def api_getDocuments():
    content = request.get_json()
    result = getDocuments( content['query'], content.get('indexName','ap_snippets_100w')  )
    #TODO: could "to_json" here if jsonify doesn't work well
    return jsonify( result ) #result.to_json #

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')