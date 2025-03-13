import React, { useEffect, useState } from 'react';
import './App.css';

interface Item {
  id: number;
  name: string;
  description?: string | null;
  price: number;
  in_stock: boolean;
}

function App() {
  const [items, setItems] = useState<Item[]>([]);
  const [newItem, setNewItem] = useState({ id: '', name: '', description: '', price: '', in_stock: true });
  const [updateItem, setUpdateItem] = useState({ id: '', name: '', description: '', price: '', in_stock: true });
  const [message, setMessage] = useState('');
  const [createErrors, setCreateErrors] = useState({ id: '', name: '', price: '' });
  const [updateErrors, setUpdateErrors] = useState({ id: '', name: '', price: '' });

  useEffect(() => {
    fetchItems();
  }, []);

  const fetchItems = async () => {
    try {
      const response = await fetch('http://localhost:8000/items/1');
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const data: Item = await response.json();
      setItems([data]);
    } catch (error: unknown) {
      setMessage(error instanceof Error ? `Error: ${error.message}` : 'Unknown error');
    }
  };

  const validateInput = (input: { id: string; name: string; price: string }) => {
    const errors = { id: '', name: '', price: '' };
    let isValid = true;

    // ID: Must be a positive integer
    if (!input.id || isNaN(Number(input.id)) || Number(input.id) <= 0) {
      errors.id = 'ID must be a positive number';
      isValid = false;
    }

    // Name: Required, non-empty
    if (!input.name.trim()) {
      errors.name = 'Name is required';
      isValid = false;
    }

    // Price: Must be a positive number
    if (!input.price || isNaN(Number(input.price)) || Number(input.price) <= 0) {
      errors.price = 'Price must be a positive number';
      isValid = false;
    }

    return { isValid, errors };
  };

  const handleCreate = async () => {
    const { isValid, errors } = validateInput(newItem);
    setCreateErrors(errors);

    if (!isValid) {
      setMessage('Please fix the errors above');
      return;
    }

    const payload: Item = {
      id: parseInt(newItem.id),
      name: newItem.name,
      description: newItem.description || null,
      price: parseFloat(newItem.price),
      in_stock: newItem.in_stock,
    };
    try {
      const response = await fetch('http://localhost:8000/items/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const data: Item = await response.json();
      setItems([...items, data]);
      setNewItem({ id: '', name: '', description: '', price: '', in_stock: true });
      setMessage('Item created!');
      setCreateErrors({ id: '', name: '', price: '' });
    } catch (error: unknown) {
      setMessage(error instanceof Error ? `Error: ${error.message}` : 'Unknown error');
    }
  };

  const handleUpdate = async () => {
    const { isValid, errors } = validateInput(updateItem);
    setUpdateErrors(errors);

    if (!isValid) {
      setMessage('Please fix the errors above');
      return;
    }

    const payload: Item = {
      id: parseInt(updateItem.id),
      name: updateItem.name,
      description: updateItem.description || null,
      price: parseFloat(updateItem.price),
      in_stock: updateItem.in_stock,
    };
    try {
      const response = await fetch(`http://localhost:8000/items/${updateItem.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const data = await response.json();
      setItems(items.map(item => (item.id === payload.id ? data.item : item)));
      setUpdateItem({ id: '', name: '', description: '', price: '', in_stock: true });
      setMessage('Item updated!');
      setUpdateErrors({ id: '', name: '', price: '' });
    } catch (error: unknown) {
      setMessage(error instanceof Error ? `Error: ${error.message}` : 'Unknown error');
    }
  };

  const handleDelete = async (id: number) => {
    try {
      const response = await fetch(`http://localhost:8000/items/${id}`, { method: 'DELETE' });
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      await response.json();
      setItems(items.filter(item => item.id !== id));
      setMessage('Item deleted!');
    } catch (error: unknown) {
      setMessage(error instanceof Error ? `Error: ${error.message}` : 'Unknown error');
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Item Manager</h1>
        <p>{message}</p>

        <h2>Create Item</h2>
        <input placeholder="ID" value={newItem.id} onChange={e => setNewItem({ ...newItem, id: e.target.value })} />
        <span style={{ color: 'red' }}>{createErrors.id}</span>
        <input placeholder="Name" value={newItem.name} onChange={e => setNewItem({ ...newItem, name: e.target.value })} />
        <span style={{ color: 'red' }}>{createErrors.name}</span>
        <input placeholder="Description" value={newItem.description} onChange={e => setNewItem({ ...newItem, description: e.target.value })} />
        <input placeholder="Price" value={newItem.price} onChange={e => setNewItem({ ...newItem, price: e.target.value })} />
        <span style={{ color: 'red' }}>{createErrors.price}</span>
        <label>
          In Stock:
          <input type="checkbox" checked={newItem.in_stock} onChange={e => setNewItem({ ...newItem, in_stock: e.target.checked })} />
        </label>
        <button onClick={handleCreate}>Add Item</button>

        <h2>Update Item</h2>
        <input placeholder="ID" value={updateItem.id} onChange={e => setUpdateItem({ ...updateItem, id: e.target.value })} />
        <span style={{ color: 'red' }}>{updateErrors.id}</span>
        <input placeholder="Name" value={updateItem.name} onChange={e => setUpdateItem({ ...updateItem, name: e.target.value })} />
        <span style={{ color: 'red' }}>{updateErrors.name}</span>
        <input placeholder="Description" value={updateItem.description} onChange={e => setUpdateItem({ ...newItem, description: e.target.value })} />
        <input placeholder="Price" value={updateItem.price} onChange={e => setUpdateItem({ ...updateItem, price: e.target.value })} />
        <span style={{ color: 'red' }}>{updateErrors.price}</span>
        <label>
          In Stock:
          <input type="checkbox" checked={updateItem.in_stock} onChange={e => setUpdateItem({ ...updateItem, in_stock: e.target.checked })} />
        </label>
        <button onClick={handleUpdate}>Update Item</button>

        <h2>Items</h2>
        <ul>
          {items.map(item => (
            <li key={item.id}>
              {item.id}: {item.name} - {item.description || 'No desc'} - ${item.price} - {item.in_stock ? 'In Stock' : 'Out of Stock'}
              <button onClick={() => handleDelete(item.id)}>Delete</button>
            </li>
          ))}
        </ul>
      </header>
    </div>
  );
}

export default App;