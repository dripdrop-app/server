import { Link } from 'react-router-dom';

interface RouterLinkProps {
	to: string;
	color?: string;
	children: JSX.Element | string;
}

const RouterLink = (props: RouterLinkProps) => {
	return (
		<Link style={{ textDecoration: 'none', color: props.color ?? 'inherit' }} to={props.to}>
			{props.children}
		</Link>
	);
};

export default RouterLink;
