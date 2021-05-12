import argparse
import os
import json
import numpy as np
import string
import nltk

from nltk.corpus import stopwords

stopwords = stopwords.words('english')

# text preprocessing
def preprocess(text):
    text = ''.join([word for word in text if word not in string.punctuation])
    text = text.lower()
    text = ' '.join([word for word in text.split() if word not in stopwords])
    return text


# obtain vector from document
def csim(texts):
	cleaned = list(map(preprocess, texts))
	vectorizer = CountVectorizer().fit_transform(cleaned)
	vectors = vectorizer.toarray()
	vector0 = vectors[0].reshape(1, -1)
	vector1 = vectors[1].reshape(1, -1)
	return cosine_similarity(vector0, vector1)[0][0]


def decode(decode_path, output):
	d = json.JSONDecoder()
	output = open(f'results{output}', 'w')

	# save data from jsonl file and write to results txt file
	with open(decode_path, 'r') as file:
		for line in file:
			results, texts = [], []
			record = d.decode(line)
			for key, value in record.items():
				if key == 'url':
					results.append('>>> URL: ' + value + '\n')
				elif key == 'title':
					results.append('>>> TITLE: ' + value + '\n')
				elif key == 'publish_date':
					results.append('>>> DATE: ' + value + '\n')
				elif key == 'summary':
					if value:
						results.append('>>> SUMMARY: ' + value + '\n')
					else:
						results.append('>>> SUMMARY: \n')
				elif key == 'text':
					results.append('>>> TEXT: ' + value + '\n')
					texts.append(value)
				elif key == 'gens_article':
					results.append('>>> GROVER: ' + value[0] + '\n')
					texts.append(value[0])

			results.append('>>> COSINE: ' + str(csim(texts)) + '\n\n')

			for line in results:
				output.write(line)

	output.close()


def main():
	# command line arguments
	parser = argparse.ArgumentParser()
	parser.add_argument('--path', type=str, help='requires path to .jsonl file in /decode')
	args = parser.parse_args()

	# decode data from Grover generation
	decode_path = f'{os.path.dirname(os.path.abspath(__file__))}/decode{args.path}.jsonl'
	decode(decode_path, f'{args.path}.txt')


if __name__ == '__main__':
	main()