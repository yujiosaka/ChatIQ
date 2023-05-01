# THREAD_TS is set to a placeholder value. This is a workaround to a constraint in the vectorstore service, which is
# backed by Weaviate. Usually, the vectorstore service excludes messages in the same thread from search results because
# they are already included in the prompt. However, we want to include file type documents in the search results.
# Due to the potentially large size of file content, we cannot simply include all file content in the prompt.
# By setting THREAD_TS to a dummy value, we ensure file type documents are not excluded by the thread filter in the
# vectorstore service.
FILE_DOCUMENT_THREAD_TS = "0000000000.000000"
