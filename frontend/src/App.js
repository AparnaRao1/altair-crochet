// frontend/src/App.js

import { useEffect, useMemo, useRef, useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [products, setProducts] = useState([]);
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("All");

  const [cart, setCart] = useState(() => {
    const saved = localStorage.getItem("altair_cart");
    return saved ? JSON.parse(saved) : [];
  });

  const [chatOpen, setChatOpen] = useState(false);
  const [message, setMessage] = useState("");

  const [chat, setChat] = useState([
    {
      from: "bot",
      text: "Welcome to Altair Crochet. Ask about dispatch, products, custom colours or recommendations."
    }
  ]);

  const chatEndRef = useRef(null);

  useEffect(() => {
    axios.get("http://127.0.0.1:5000/products")
      .then(res => setProducts(res.data))
      .catch(err => console.log(err));
  }, []);

  useEffect(() => {
    localStorage.setItem("altair_cart", JSON.stringify(cart));
  }, [cart]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({
      behavior: "smooth"
    });
  }, [chat]);

  const categories = useMemo(() => {
    const unique = [...new Set(products.map(p => p.category))];
    return ["All", ...unique];
  }, [products]);

  const filtered = products.filter(item => {
    const a = item.name.toLowerCase().includes(search.toLowerCase());
    const b = category === "All" || item.category === category;
    return a && b;
  });

  const addToCart = (item) => {
    const existing = cart.find(c => c.id === item.id);

    if (existing) {
      if (existing.qty >= 20) return;

      setCart(cart.map(c =>
        c.id === item.id
          ? { ...c, qty: c.qty + 1 }
          : c
      ));
    } else {
      setCart([...cart, { ...item, qty: 1 }]);
    }
  };

  const increaseQty = (id) => {
    setCart(cart.map(item =>
      item.id === id && item.qty < 20
        ? { ...item, qty: item.qty + 1 }
        : item
    ));
  };

  const decreaseQty = (id) => {
    setCart(cart.flatMap(item => {
      if (item.id !== id) return item;
      if (item.qty === 1) return [];
      return { ...item, qty: item.qty - 1 };
    }));
  };

  const removeItem = (id) => {
    setCart(cart.filter(item => item.id !== id));
  };

  const total = cart.reduce(
    (sum, item) => sum + item.price * item.qty,
    0
  );

  const totalItems = cart.reduce(
    (sum, item) => sum + item.qty,
    0
  );

  const checkout = () => {
    const lines = cart.map(
      item => `${item.name} x${item.qty} = ₹${item.qty * item.price}`
    ).join("%0A");

    const url =
      `https://wa.me/916364244719?text=Order Request%0A%0A${lines}%0A%0ATotal: ₹${total}`;

    window.open(url, "_blank");
  };

  const sendMessage = async () => {
    if (!message.trim()) return;

    const userText = message;

    setChat(prev => [
      ...prev,
      { from: "user", text: userText }
    ]);

    setMessage("");

    try {
      const res = await axios.post(
        "http://127.0.0.1:5000/chat",
        { message: userText }
      );

      setChat(prev => [
        ...prev,
        { from: "bot", text: res.data.reply }
      ]);
    } catch {
      setChat(prev => [
        ...prev,
        {
          from: "bot",
          text: "Connection issue. Please ensure backend server is running."
        }
      ]);
    }
  };

  return (
    <div className="app">

      <header className="header">
        <h1>ALTAIR CROCHET</h1>
        <div className="cartCount">
          Cart ({totalItems})
        </div>
      </header>

      <section className="toolbar">
        <input
          type="text"
          placeholder="Search products"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />

        <select
          value={category}
          onChange={(e) => setCategory(e.target.value)}
        >
          {categories.map(cat => (
            <option key={cat}>{cat}</option>
          ))}
        </select>
      </section>

      <section className="layout">

        <div className="products">
          {filtered.map(item => (
            <div className="card" key={item.id}>
              <img src={item.image} alt={item.name} />

              <div className="cardBody">
                <h3>{item.name}</h3>
                <p>{item.description}</p>
                <h2>₹{item.price}</h2>

                <button onClick={() => addToCart(item)}>
                  Add to Cart
                </button>
              </div>
            </div>
          ))}
        </div>

        <aside className="cartPanel">

          <h2>Cart</h2>

          {cart.length === 0 && (
            <p className="empty">No items added.</p>
          )}

          {cart.map(item => (
            <div className="cartItem" key={item.id}>
              <div>
                <strong>{item.name}</strong>
                <p>₹{item.price}</p>
              </div>

              <div className="qtyBox">
                <button onClick={() => decreaseQty(item.id)}>-</button>
                <span>{item.qty}</span>
                <button onClick={() => increaseQty(item.id)}>+</button>
              </div>

              <button
                className="removeBtn"
                onClick={() => removeItem(item.id)}
              >
                Remove
              </button>
            </div>
          ))}

          <div className="summary">
            <h3>Total ₹{total}</h3>

            {cart.length > 0 && (
              <button className="checkout" onClick={checkout}>
                Checkout
              </button>
            )}
          </div>

          <div className="assistantSection">
            <button
              className="chatToggle"
              onClick={() => setChatOpen(true)}
            >
              Assistant
            </button>
          </div>

        </aside>

      </section>

      {chatOpen && (
        <div className="chatWindow">

          <div className="chatTopBar">
            <span>Altair Assistant</span>

            <button
              className="closeChat"
              onClick={() => setChatOpen(false)}
            >
              ×
            </button>
          </div>

          <div className="chatBody">
            {chat.map((msg, index) => (
              <div
                key={index}
                className={
                  msg.from === "user"
                    ? "bubble userBubble"
                    : "bubble botBubble"
                }
              >
                {msg.text}
              </div>
            ))}

            <div ref={chatEndRef}></div>
          </div>

          <div className="chatBottom">
            <input
              type="text"
              placeholder="Type a message"
              value={message}
              onChange={(e) =>
                setMessage(e.target.value)
              }
              onKeyDown={(e) =>
                e.key === "Enter" && sendMessage()
              }
            />

            <button onClick={sendMessage}>
              Send
            </button>
          </div>

        </div>
      )}

    </div>
  );
}

export default App;