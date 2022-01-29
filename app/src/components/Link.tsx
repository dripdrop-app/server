import { Button } from '@mui/material';
import { useMemo } from 'react';
import { Link } from 'react-router-dom';
import { Link as MaterialLink } from '@mui/material';

interface CustomLinkProps {
	text: string | JSX.Element;
	to?: string;
	href?: string;
	textColor?: string;
	button?: boolean;
	useMaterial?: boolean;
}

const CustomLink = (props: CustomLinkProps) => {
	const linkStyle = useMemo(
		() => ({
			color: props.textColor,
			textDecoration: 'none',
		}),
		[props.textColor]
	);

	const linkProps = useMemo(
		() => ({
			to: props.to,
			href: props.href,
			target: props.href ? '_blank' : '',
		}),
		[props.href, props.to]
	);

	const link = props.useMaterial ? (
		<MaterialLink style={linkStyle} {...linkProps}>
			{props.text}
		</MaterialLink>
	) : (
		<Link style={linkStyle} {...linkProps}>
			{props.text}
		</Link>
	);

	if (props.button) {
		return <Button color="inherit">{link}</Button>;
	}

	return link;
};

export default CustomLink;
