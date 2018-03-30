from vdv.MediaResolver.ImageResolver import ImageResolver

class MediaResolverFactory:
    resolvers = {'image': ImageResolver}
    separator = '\r\n'.encode()
    @staticmethod
    def produce(type, data):
        if type in MediaResolverFactory.resolvers:
            return MediaResolverFactory.resolvers[type](data)

