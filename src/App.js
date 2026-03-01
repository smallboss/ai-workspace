
import { ToastContainer } from 'react-toastify';
import './App.css';
import 'react-toastify/dist/ReactToastify.css';
import Aviator from './components/aviator';
import SVGs from './components/svgs'
import AviatorProvider from './store/aviator'
import { BrowserRouter, Route, Routes } from "react-router-dom";
function App() {
  return (
    <>
      <ToastContainer
        position="top-right"
        autoClose={5000}
        hideProgressBar={false}
        newestOnTop={false}
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
        theme="colored"
      />
      <SVGs />
      <AviatorProvider>
        <BrowserRouter>
          <Routes>
            <Route path="aviator">
              <Route index element={<Aviator />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </AviatorProvider>
    </>
  );
}

export default App;
