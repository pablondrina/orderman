function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function confirmCancellation(event, orderId) {
    event.preventDefault();
    if (confirm(`Tem certeza que deseja cancelar o pedido #${orderId}?`)) {
        const url = event.target.closest('a').href;
        fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ order_id: orderId })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Recarrega a página sem ativar o drawer de filtragem
                window.location.reload();
            } else {
                alert('Erro ao cancelar o pedido: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Erro:', error);
            alert('Ocorreu um erro ao tentar cancelar o pedido.');
        });
    }
    return false;
}


document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM carregado, iniciando conexão WebSocket...');
    const socket = new WebSocket('ws://' + window.location.host + '/ws/orders/');

    socket.onopen = function(e) {
        console.log('Conexão WebSocket estabelecida com sucesso');
    };

    socket.onerror = function(error) {
        console.error('Erro na conexão WebSocket:', error);
    };

    socket.onclose = function(e) {
        console.log('Conexão WebSocket fechada. Código:', e.code, 'Razão:', e.reason);
    };

    socket.onmessage = function(e) {
        console.log('Mensagem WebSocket recebida:', e.data);
        const data = JSON.parse(e.data);
        if (data.message === 'new_order') {
            console.log('Novo pedido detectado, atualizando lista...');
            updateOrderList();
        }
    };

    function updateOrderList() {
        console.log('Iniciando atualização da lista de pedidos...');
        htmx.ajax('GET', window.location.href, '#result_list tbody')
            .then(() => {
                console.log('Lista de pedidos atualizada com sucesso');
            })
            .catch((error) => {
                console.error('Erro ao atualizar lista de pedidos:', error);
            });
    }
});