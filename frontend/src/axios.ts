// axios.js

import axios from 'axios';

const instance = axios.create({
  baseURL: 'http://localhost:8000', // Replace this with your backend's base URL
});

export default instance;
