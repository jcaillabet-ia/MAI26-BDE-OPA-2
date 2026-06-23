const apiUrl = 'http://localhost:8000';

document.addEventListener('alpine:init', () => {
    Alpine.data('pageIndex', () => ({
        // messages: [],
        // ws: null,

        init() {
            // fetch('/api/messages')
            //     .then(res => res.json())
            //     .then(data => this.messages = data);

            // this.ws = new WebSocket('ws://localhost:3000');
            // this.ws.onmessage = (event) => {
            //     this.messages.push(event.data);
            // };
        },

        enableCoin(id) {
            // this.ws.send('Hello !');
            fetch(`${apiUrl}/coin/${id}/enable`, {
                method: 'PATCH',
            })
                .then(res => res.json())
                .then(data => console.log(data));
        }
    }));
});
