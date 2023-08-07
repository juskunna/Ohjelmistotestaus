export function Overlay({close, headerTitle, children}) {

    return (
        <div className="overlay">
            <div className="create-todo">
                <div className="create-header">
                    <p>{headerTitle}</p>
                    <p onClick={close}>X</p>
                </div>
                {children}
                <button onClick={close}>Peruuta</button>
            </div>
        </div>
    );
}