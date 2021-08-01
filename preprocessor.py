from Dataset import Dataset

original_dataset_path = 'PATH-TO-RAW-DATASET'
processed_dataset_path = 'PATH-TO-PROCESSED-DATASET'

individuals = ['allen-p', 'arnold-j', 'arora-h', 'watson-k',
               'badeer-r', 'bailey-s', 'bass-e', 'dean-c',
               'baughman-d', 'beck-s', 'benson-r', 'davis-d',
               'meyers-a', 'carson-m', 'jones-t', 'hernandez-j',
               'shapiro-r', 'shively-h', 'slinger-r', 'solberg-g',
               'thomas-p', 'ward-k', 'zipper-a', 'parks-j',
               'sanders-r', 'staab-t', 'tholt-j', 'whitt-m',
               'scott-s', 'white-s', 'wolfe-j', 'smith-m']

# Load raw dataset and preprocess
ds = Dataset.parse_dataset(original_dataset_path, individuals)
ds.generate_dict()
ds.generate_doc_bow()

# Save processed dataset for future use
ds.save_dictionary(processed_dataset_path)
ds.save_processed_dataset(processed_dataset_path)

# Load processed dataset
# ds = Dataset.load_processed_dataset(processed_dataset_path, individuals)
# ds.load_dictionary(processed_dataset_path)

print('dict size: ', ds.get_dict_size())
print('total mails count: ', ds.get_mails_count())
print('individuals count: ', ds.get_individuals_count())

for i in ds.get_all():
    print('{0}, inbox: {1}, deleted: {2} '.format(
        i.name, i.get_inbox_mail_count(), i.get_deleted_mail_count()))
