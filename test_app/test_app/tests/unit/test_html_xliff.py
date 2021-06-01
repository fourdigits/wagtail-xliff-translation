def test_flat_html(html_parser):
    html_parser.feed(
        "<a>hello world</a>hoebakek<ol><li>item_1</li><li>item_2</li></ol>"
    )
    assert html_parser.content_list == ["hello world", "hoebakek", "item_1", "item_2"]
    assert (
        html_parser.html
        == "<a>{placeholder_0}</a>{placeholder_1}<ol><li>{placeholder_2}</li><li>{placeholder_3}</li></ol>"
    )
    assert (
        html_parser.encode_html()
        == "PGE+e3BsYWNlaG9sZGVyXzB9PC9hPntwbGFjZWhvbGRlcl8xfTxvbD48bGk+e3BsYWNlaG9sZGVyXzJ9PC9saT48bGk+e3BsYWNlaG9sZGVyXzN9PC9saT48L29sPg=="
    )

    html_parser.reset()
    html = """
    <div class="rich-text">
        <h2>Header2</h2>
        <ul class="None">
            <li>List item 1</li>
            <li>List item 2
                <ul>
                    <li>Deeper item 1</li>
                    <li>
                        <br class="break" />
                        <br />
                        Item with double break</li>
                </ul>
            </li>
        </ul>
        <hr />
        <p>
            <b>Bold item after HR</b>
            <img src="test/123/image.jpg" />
        </p>
        <p>
            <a href="https://test.com" follow>Link item</a>
        </p>
    </div>
    """
    html_parser.feed(html)
    assert '<div class="rich-text">' in html_parser.html
    assert "</div>" in html_parser.html

    html_parser.encode_html()
    # Encoding the html returns a new html string and does not replace the other
    assert '<div class="rich-text">' in html_parser.html
    assert "</div>" in html_parser.html

    assert html_parser.html
    assert html_parser.content_list

    # There are 7 data items, so placeholder 0-6 need to be in the HTML
    assert "{placeholder_0}" in html_parser.html
    assert "{placeholder_6}" in html_parser.html

    html_parser.reset()

    assert not html_parser.html
    assert not html_parser.content_list
