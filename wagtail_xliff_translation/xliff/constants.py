class ContentType:
    DOCUMENT = "local:document"
    STRUCTURAL_FLAT = "local:structural-flat"
    STREAM = "local:stream"
    STRUCTURAL = "local:structural"
    FLAT = "local:flat"
    TEXT = "local:text"
    RICHTEXTFIELD = "local:RichTextField"


class XliffElements:
    TEXT = "#text"
    GROUP = "group"
    DATA = "data"
    ORIGINAL_DATA = "originalData"
    PH = "ph"
    PC = "pc"
    SOURCE = "source"
    TARGET = "target"
    SEGMENT = "segment"
    UNIT = "unit"
    META = "mda:meta"
    METAGROUP = "mda:metaGroup"
    METADATA = "mda:metadata"
    FILE = "file"
    XLIFF = "xliff"
    HEADER = "header"
    INTERNAL_FILE = "internal_file"


class XliffAttributes:
    TRGLANG = "trgLang"
    SRCLANG = "srcLang"


class FileAttributes:
    ID = "id"


class DataAttributes(FileAttributes):
    pass


class PcAttributes(FileAttributes):
    DATAREFEND = "dataRefEnd"
    DATAREFSTART = "dataRefStart"


class PhAttributes(FileAttributes):
    DATAREF = "dataRef"


class MetaGroupAttributes:
    CATEGORY = "category"


class MetaAttributes:
    TYPE = "type"


class TranslationAttributes:
    CAN_RESEGMENT = "canResegment"
    ID = "id"
    TYPE = "type"
    NAME = "name"
    TRANSLATE = "translate"


class UnitAttributes(TranslationAttributes):
    SIZE_RESTRICTION = "slr:sizeRestriction"


class GroupAttributes(TranslationAttributes):
    pass
