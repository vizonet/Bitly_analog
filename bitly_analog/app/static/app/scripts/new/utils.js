/* ����� ������� ��� ��������������� ������� ������ */

let full,   // ���� ������ ������
    domain,     // ���� ������
    subpart;    // ���� ���������

function let_short() {
    /* Ajax GET-������ � ���������� ������ ������. 
     * ���������� JSON-������� ��������� �������� ������ � ��������� {'domain': <domain>, 'subpart': <subpart>}. 
     * */

    // DOM-������� ������ �� ��������� ����  
    let url = document.createElement('a');
    url.href = full.value;

    // ��������� ������ ������ �� ������ �� ������������ ������ �������� 'a' - ['href','protocol','host','hostname','port','pathname','search','hash']

    // ���������� ������
    // let re = /https?:\/\/(?:[-\w]+\.)?([-\w]+)\.\w+(?:\.\w+)?\/?.*/i
    let domain_str = url['hostname'].replace('www', '');
    domain.value = domain_str;

    // ���������� ���������
    let re = /[^\/]+/ig                                                     
    let subpart_str = url['pathname'].match(re)[0];
    subpart.value = subpart_str;


    // GET-������ ��� �������� ������������ ��������� � ��
    let path = 'check_subpart/' + subpart_str;
    fetch_get(path)
        .then(
            
        )

    // POST-������ ��� ������ �������� ������ � �� 
    data = {
        'url': full.value,
        'domain': domain_str,
        'subpart': subpart_str,
    }

    fetch_post('url_ajax')
        .then(
            // �������� ������� �� �������
        )
}

// ��������� ��������� �� ������� �������� DOM-������
document.addEventListener("DOMContentLoaded", function () {
    // C���� � ������ �����
    full = document.getElementById('id_full');
    domain = document.getElementById('id_domain');
    subpart = document.getElementById('id_subpart');

    // ��������� ����������� �� ������� ����� ������ � ���� ������ ������
    full.addEventListener('input', let_short());
    
    // ��������� ����������� �� ������� ����� ������ � ���� ���������
    subpart.addEventListener('input', let_short()); 
})