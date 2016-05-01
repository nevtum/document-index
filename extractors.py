class ContentExtractorMixin:
    def extension_filter():
        raise NotImplemented("Override this method!")

    @staticmethod
    def get_contents(filename):
        raise NotImplemented("Override this method!")
        
class TextExtractor(ContentExtractorMixin):
    @staticmethod
    def extension_filter():
        return "*.txt"

    @staticmethod
    def get_contents(filename):
        with open(filename, 'rb') as stream:
            return stream.read()