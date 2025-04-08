import { useNavigate } from "react-router-dom";

const Footer = () => {
  const navigate = useNavigate();

  return (
    <footer className="p-4 text-center text-gray-400 text-sm mt-10 mb-6">
      <p>
        Tailor{' '}

        {/* <span 
          onClick={() => navigate("/terms")}
          className="underline hover:text-white cursor-pointer"
        >
          Terms & Conditions
        </span> */}

        {/* {' '}and our{' '} */}

        <span 
          onClick={() => navigate("/privacy")}
          className="underline hover:text-white cursor-pointer"
        >
          Privacy Policy
        </span>
      </p>
    </footer>
  );
};

export default Footer;
