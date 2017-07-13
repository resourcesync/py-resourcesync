# `mock_responses` is a list of dictionaries, indexed by the test number (in `test_oaipmh_generator.py`) in which they're referenced.
# Each dictionary maps mock HTTP GET target URLs to the corresponding mock text/xml response body.

mock_responses = [
    {
        "http://example.com/oai?verb=GetRecord&identifier=A&metadataPrefix=oai_dc": """
<?xml version="1.0" encoding="UTF-8"?>
<OAI-PMH xmlns="http://www.openarchives.org/OAI/2.0/"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/
                             http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd">
  <responseDate>1970-01-02T00:00:00Z</responseDate>
  <request verb="GetRecord" metadataPrefix="oai_dc" identifier="A">http://example.com/oai</request>
  <GetRecord>
    <record>
      <header>
        <identifier>A</identifier>
        <datestamp>1970-01-01T00:00:00Z</datestamp>
      </header>
      <metadata>
        <oai_dc:dc xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/"
                   xmlns:dc="http://purl.org/dc/elements/1.1/"
                   xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                   xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/oai_dc/
                                       http://www.openarchives.org/OAI/2.0/oai_dc.xsd">
          <dc:title>test</dc:title>
        </oai_cd:dc>
      </metadata>
    </record>
  </GetRecord>
</OAI-PMH>
        """,

        "http://example.com/oai?verb=GetRecord&identifier=B&metadataPrefix=oai_dc": """
<?xml version="1.0" encoding="UTF-8"?>
<OAI-PMH xmlns="http://www.openarchives.org/OAI/2.0/"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/
                             http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd">
  <responseDate>1970-01-02T00:00:00Z</responseDate>
  <request verb="GetRecord" metadataPrefix="oai_dc" identifier="B">http://example.com/oai</request>
  <GetRecord>
    <record>
      <header>
        <identifier>B</identifier>
        <datestamp>1970-01-01T00:00:00Z</datestamp>
      </header>
      <metadata>
        <oai_dc:dc xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/"
                   xmlns:dc="http://purl.org/dc/elements/1.1/"
                   xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                   xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/oai_dc/
                                       http://www.openarchives.org/OAI/2.0/oai_dc.xsd">
          <dc:title>test</dc:title>
        </oai_cd:dc>
      </metadata>
    </record>
  </GetRecord>
</OAI-PMH>
        """,

        "http://example.com/oai?verb=ListIdentifiers&set=test&metadataPrefix=oai_dc": """
<?xml version="1.0" encoding="UTF-8"?>
<OAI-PMH xmlns="http://www.openarchives.org/OAI/2.0/"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/
                             http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd">
  <responseDate>1970-01-02T00:00:00Z</responseDate>
  <request verb="ListIdentifiers" metadataPrefix="oai_dc">http://example.com/oai</request>
  <ListIdentifiers>
    <header>
      <identifier>A</identifier>
      <datestamp>1970-01-01T00:00:00Z</datestamp>
      <setSpec>test</setSpec>
    </header>
    <header>
      <identifier>B</identifier>
      <datestamp>1970-01-01T00:00:00Z</datestamp>
      <setSpec>test</setSpec>
    </header>
  </ListIdentifiers>
</OAI-PMH>
        """
    },
    {
        "http://example.com/oai?verb=GetRecord&identifier=A&metadataPrefix=oai_dc": """
<?xml version="1.0" encoding="UTF-8"?>
<OAI-PMH xmlns="http://www.openarchives.org/OAI/2.0/"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/
                             http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd">
  <responseDate>1970-01-04T00:00:00Z</responseDate>
  <request verb="GetRecord" metadataPrefix="oai_dc" identifier="A">http://example.com/oai</request>
  <GetRecord>
    <record>
      <header status="deleted">
        <identifier>A</identifier>
        <datestamp>1970-01-03T00:00:00Z</datestamp>
      </header>
    </record>
  </GetRecord>
</OAI-PMH>
        """,

        "http://example.com/oai?verb=GetRecord&identifier=B&metadataPrefix=oai_dc": """
<?xml version="1.0" encoding="UTF-8"?>
<OAI-PMH xmlns="http://www.openarchives.org/OAI/2.0/"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/
                             http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd">
  <responseDate>1970-01-04T00:00:00Z</responseDate>
  <request verb="GetRecord" metadataPrefix="oai_dc" identifier="B">http://example.com/oai</request>
  <GetRecord>
    <record>
      <header>
        <identifier>B</identifier>
        <datestamp>1970-01-03T00:00:00Z</datestamp>
      </header>
      <metadata>
        <oai_dc:dc xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/"
                   xmlns:dc="http://purl.org/dc/elements/1.1/"
                   xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                   xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/oai_dc/
                                       http://www.openarchives.org/OAI/2.0/oai_dc.xsd">
          <dc:title>update</dc:title>
        </oai_cd:dc>
      </metadata>
    </record>
  </GetRecord>
</OAI-PMH>
        """,

        "http://example.com/oai?verb=GetRecord&identifier=C&metadataPrefix=oai_dc": """
<?xml version="1.0" encoding="UTF-8"?>
<OAI-PMH xmlns="http://www.openarchives.org/OAI/2.0/"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/
                             http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd">
  <responseDate>1970-01-04T00:00:00Z</responseDate>
  <request verb="GetRecord" metadataPrefix="oai_dc" identifier="C">http://example.com/oai</request>
  <GetRecord>
    <record>
      <header>
        <identifier>C</identifier>
        <datestamp>1970-01-03T00:00:00Z</datestamp>
      </header>
      <metadata>
        <oai_dc:dc xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/"
                   xmlns:dc="http://purl.org/dc/elements/1.1/"
                   xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                   xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/oai_dc/
                                       http://www.openarchives.org/OAI/2.0/oai_dc.xsd">
          <dc:title>create</dc:title>
        </oai_cd:dc>
      </metadata>
    </record>
  </GetRecord>
</OAI-PMH>
        """,

        "http://example.com/oai?verb=ListIdentifiers&set=test&metadataPrefix=oai_dc": """
<?xml version="1.0" encoding="UTF-8"?>
<OAI-PMH xmlns="http://www.openarchives.org/OAI/2.0/"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/
                             http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd">
  <responseDate>1970-01-04T00:00:00Z</responseDate>
  <request verb="ListIdentifiers" metadataPrefix="oai_dc">http://example.com/oai</request>
  <ListIdentifiers>
    <header status="deleted">
      <identifier>A</identifier>
      <datestamp>1970-01-03T00:00:00Z</datestamp>
      <setSpec>test</setSpec>
    </header>
    <header>
      <identifier>B</identifier>
      <datestamp>1970-01-03T00:00:00Z</datestamp>
      <setSpec>test</setSpec>
    </header>
    <header>
      <identifier>C</identifier>
      <datestamp>1970-01-03T00:00:00Z</datestamp>
      <setSpec>test</setSpec>
    </header>
  </ListIdentifiers>
</OAI-PMH>
        """
    }
]
