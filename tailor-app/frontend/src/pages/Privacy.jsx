import './Privacy.css';

const Privacy = () => {
    return (
        <div className="privacy-policy-container">
          <h1 className="privacy-policy-title">Privacy Policy</h1>
    
          <p className="intro">
            Tailor respects your privacy. This Privacy Policy explains how we collect, use, and protect your information when using our services, particularly with regard to data retrieved from Pinterest.
          </p>
    
          <section className="section">
            <h2 className="section-title">Information We Collect</h2>
            <p className="section-content">
              Our app retrieves publicly available Pins from Pinterest based on user-provided search keywords. The data we collect includes:
            </p>
            <ul className="section-list">
              <h4>Pin ID</h4>
              <h4>Image URL</h4>
              <h4>Dominant colors of the image</h4>
              <h4>Pin description</h4>
            </ul>
            <p className="section-content">
              We do <strong>not</strong> access or store any personal Pinterest account information.
            </p>
          </section>
    
          <section className="section">
            <h2 className="section-title">How We Use Your Information</h2>
            <p className="section-content">We use Pinterest data to:</p>
            <ul className="section-list">
              <h4>Populate mood boards based on the user’s selected aesthetic.</h4>
              <h4>Analyze images using the Cohere API to enhance recommendations and content insights.</h4>
              <h4>Improve user experience by curating relevant mood board content.</h4>
            </ul>
          </section>
    
          <section className="section">
            <h2 className="section-title">How We Share Your Information</h2>
            <p className="section-content">We may share collected Pinterest data in the following cases:</p>
            <ul className="section-list">
              <h4><strong>With Cohere API:</strong> To analyze images and generate insights.</h4>
            </ul>
            <p className="section-content">
              We <strong>do not</strong> sell or share user data for advertising or marketing purposes.
            </p>
          </section>
    
          <section className="section">
            <h2 className="section-title">Data Storage & User Control</h2>
            <p className="section-content">
              Retrieved Pins are stored in our app until the user chooses to delete them.
            </p>
            <p className="section-content">
              Users can remove any saved Pins from their mood boards at any time.
            </p>
          </section>
    
          <section className="section">
            <h2 className="section-title">Security Measures</h2>
            <p className="section-content">
              We implement industry-standard security measures, including encrypted data storage and secure API connections, to protect user data.
            </p>
          </section>
    
          <section className="section">
            <h2 className="section-title">Contact Us</h2>
            <p className="section-content">
              For any privacy-related inquiries, please contact us at:
            </p>
            <p className="contact-details">
              <strong>Email:</strong> <a href="mailto:tailorfashionai@gmail.com">tailorfashionai@gmail.com</a>
            </p>
            <p className="contact-details">
              <strong>Website:</strong> <a href="https://tailor-4d71417e9aab.herokuapp.com/" target="_blank" rel="noopener noreferrer">https://tailor-4d71417e9aab.herokuapp.com/</a>
            </p>
          </section>
        </div>
      );
};

export default Privacy;
